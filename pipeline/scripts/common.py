import json
import os
from typing import Any

import boto3

AWS_ASSUME_ROLE_ARN = "arn:aws:iam::510900713680:role/digitalorganising-cac-admin"
OPENSEARCH_CREDENTIALS_SECRET = "opensearch-credentials"
OPENSEARCH_ENDPOINT_PARAMETER_NAME = "opensearch-endpoint"
AWS_REGION = "eu-west-1"


def get_boto_session(*, role_session_name: str = "pipeline-scripts") -> boto3.Session:
    """Assume the admin role and return a boto3 session with those credentials."""
    profile = os.environ.get("AWS_PROFILE", "sso-profile")
    base = boto3.Session(profile_name=profile, region_name=AWS_REGION)
    sts = base.client("sts")
    creds = sts.assume_role(
        RoleArn=AWS_ASSUME_ROLE_ARN,
        RoleSessionName=role_session_name,
    )["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=AWS_REGION,
    )


def get_opensearch_config(session: boto3.Session) -> tuple[str, tuple[str, str]]:
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


def parse_es_query(query_str: str) -> dict[str, Any]:
    """Build an ES search body from a JSON query or query_string text."""
    query_str = query_str.strip()
    if query_str.startswith("{"):
        try:
            query = json.loads(query_str)
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON query: {e}") from e
        if "query" in query:
            return query
        return {"query": query}
    return {
        "query": {
            "query_string": {
                "query": query_str,
                "default_operator": "AND",
            }
        }
    }


def index_name(namespace: str, suffix: str | None) -> str:
    return f"{namespace}-{suffix}" if suffix else namespace
