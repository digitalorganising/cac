#!/usr/bin/env -S uv run python
"""
Reindex companies matching an Elasticsearch query.

Searches the disambiguated-companies index with the given query, collects the
original request (input) from each hit, and invokes the company-disambiguator
Lambda to re-run disambiguation and update the index.

Usage:
  reindex_companies.py '<query>'              # query_string query
  reindex_companies.py '{"match":{"input.name":"Acme"}}'  # raw query JSON
  reindex_companies.py --unidentified         # built-in unidentified query
  reindex_companies.py --unidentified --clear-existing-disambiguation

"""

import argparse
import asyncio
import json
import os
import sys

import boto3
from botocore.config import Config
from opensearchpy import helpers

BOTO_TIMEOUT = 900  # seconds

from company_disambiguator.model import DisambiguateCompanyRequest, request_to_doc_id
from pipeline.services.opensearch_utils import create_client

AWS_ASSUME_ROLE_ARN = "arn:aws:iam::510900713680:role/digitalorganising-cac-admin"
OPENSEARCH_CREDENTIALS_SECRET = "opensearch-credentials"
OPENSEARCH_ENDPOINT_PARAMETER_NAME = "opensearch-endpoint"

INDEX = "disambiguated-companies"
DEFAULT_LAMBDA_NAME = "pipeline-company-disambiguator"
BATCH_SIZE = 10


def get_boto_session():
    """Assume the admin role and return a boto3 session with those credentials."""
    profile = os.environ.get("AWS_PROFILE", "sso-profile")
    base = boto3.Session(profile_name=profile, region_name="eu-west-1")
    sts = base.client("sts")
    creds = sts.assume_role(
        RoleArn=AWS_ASSUME_ROLE_ARN,
        RoleSessionName="reindex-companies",
    )["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name="eu-west-1",
    )


def get_opensearch_config(session):
    """Fetch endpoint from Parameter Store and credentials from Secrets Manager."""
    ssm = session.client("ssm")
    param = ssm.get_parameter(
        Name=OPENSEARCH_ENDPOINT_PARAMETER_NAME, WithDecryption=True
    )
    endpoint = param["Parameter"]["Value"]

    secrets = session.client("secretsmanager")
    secret = secrets.get_secret_value(SecretId=OPENSEARCH_CREDENTIALS_SECRET)
    creds = json.loads(secret["SecretString"])
    auth = (creds["username"], creds["password"])

    return endpoint, auth


def unidentified_query() -> dict:
    """Query for companies already marked as unidentified."""
    return {"query": {"term": {"disambiguated_company.type": "unidentified"}}}


def parse_query(query_str: str) -> dict:
    """Build ES search body from user query string."""
    query_str = query_str.strip()
    if query_str.startswith("{"):
        try:
            q = json.loads(query_str)
            # Allow full query object or just the inner query
            if "query" in q:
                return q
            return {"query": q}
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON query: {e}") from e
    # Plain string: use query_string on useful fields
    return {
        "query": {
            "query_string": {
                "query": query_str,
                "fields": ["input.name"],
                "default_operator": "AND",
            }
        }
    }


def extract_requests(sources):
    """Parse DisambiguateCompanyRequest from each hit's input field."""
    requests = []
    for src in sources:
        inp = src.get("input")
        if not inp:
            continue
        try:
            requests.append(DisambiguateCompanyRequest.model_validate(inp))
        except Exception as e:
            print(f"Warning: skip invalid input {inp}: {e}", file=sys.stderr)
    return requests


async def clear_existing_disambiguation(client, requests):
    """Delete stored disambiguation fields for the selected request IDs."""

    async def clear_actions():
        for req in requests:
            yield {
                "_op_type": "update",
                "_index": INDEX,
                "_id": request_to_doc_id(req),
                "script": {
                    "lang": "painless",
                    "source": """
if (ctx._source.containsKey('disambiguated_company')) {
  ctx._source.remove('disambiguated_company');
}
""",
                },
            }

    async for ok, result in helpers.async_streaming_bulk(
        client, clear_actions(), index=INDEX, raise_on_error=False
    ):
        if not ok:
            print(f"Warning: failed to clear doc: {result}", file=sys.stderr)
    await client.indices.refresh(index=INDEX)


def invoke_lambda_sync(session, function_name: str, event: dict) -> dict:
    """Synchronously invoke the company-disambiguator Lambda."""
    config = Config(connect_timeout=BOTO_TIMEOUT, read_timeout=BOTO_TIMEOUT)
    lambda_client = session.client("lambda", config=config)
    payload = json.dumps(event)
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=payload,
    )
    payload_out = response["Payload"].read().decode()
    result = json.loads(payload_out)
    if "errorMessage" in result:
        raise RuntimeError(result.get("errorMessage"), result.get("stackTrace"))
    return result


async def main():
    parser = argparse.ArgumentParser(
        description="Reindex companies by running an ES query and invoking the company-disambiguator Lambda."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help='ES query: either a query_string (plain text) or JSON, e.g. {"match":{"input.name":"Acme"}}',
    )
    parser.add_argument(
        "--unidentified",
        action="store_true",
        help="Use a built-in query for disambiguated_company.type=unidentified",
    )
    parser.add_argument(
        "--clear-existing-disambiguation",
        action="store_true",
        help="Before reindexing, remove existing disambiguation fields from matched docs",
    )
    args = parser.parse_args()
    if not args.unidentified and not args.query:
        parser.error("query is required unless --unidentified is provided")

    session = get_boto_session()
    endpoint, auth = get_opensearch_config(session)
    client = create_client(
        cluster_host=endpoint,
        auth=auth,
        async_client=True,
    )

    try:
        body = unidentified_query() if args.unidentified else parse_query(args.query)
        print(f"Query: {json.dumps(body, indent=2)}", file=sys.stderr)
        sources = []
        async for doc in helpers.async_scan(client, index=INDEX, query=body, size=500):
            sources.append(doc.get("_source", {}))
        requests = extract_requests(sources)
        print(f"Found {len(requests)} companies to reindex", file=sys.stderr)
        if not requests:
            return
        if args.clear_existing_disambiguation:
            print(
                "Clearing existing disambiguation fields before reindex...",
                file=sys.stderr,
            )
            await clear_existing_disambiguation(client, requests)

        for i in range(0, len(requests), BATCH_SIZE):
            batch = requests[i : i + BATCH_SIZE]
            event = {
                "requests": [r.model_dump(mode="json") for r in batch],
                "force": True,
            }
            print(
                f"Invoking Lambda for batch {i // BATCH_SIZE + 1} ({len(batch)} requests)...",
                file=sys.stderr,
            )
            result = invoke_lambda_sync(session, DEFAULT_LAMBDA_NAME, event)
            print(json.dumps(result, indent=2), file=sys.stderr)
        print("Done.", file=sys.stderr)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
