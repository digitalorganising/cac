#!/usr/bin/env -S uv run python
"""
Build a Step Functions ScraperEvent JSON for re-indexing pipeline outcomes.

Queries outcomes-indexed (by default outcomes-indexed-1012), resolves matching
outcome references to raw decision document IDs in outcomes-raw, and prints a
JSON payload suitable for pasting into the AWS Step Functions console.

Example:

  uv run python scripts/reindex_outcomes.py \\
    '{"query":{"term":{"filter.state":"ballot_held"}}}'

  uv run python scripts/reindex_outcomes.py \\
  '{"query":{"match_all":{}}}' --document-type method_agreed
"""

import argparse
import asyncio
import json
import sys

from opensearchpy import helpers

from common import get_boto_session, get_opensearch_config, index_name, parse_es_query
from pipeline.services.opensearch_utils import create_client
from pipeline.types.documents import DocumentType

STEP_FUNCTIONS_INPUT_LIMIT_BYTES = 256 * 1024
REFERENCE_BATCH_SIZE = 500


async def collect_outcome_references(
    client, outcomes_index: str, query: dict
) -> list[str]:
    references: list[str] = []
    async for doc in helpers.async_scan(
        client,
        index=outcomes_index,
        query=query,
        _source=False,
    ):
        references.append(doc["_id"])
    return references


async def collect_raw_decision_ids(
    client,
    raw_index: str,
    references: list[str],
    *,
    document_type: str | None = None,
) -> list[str]:
    ids: list[str] = []
    for offset in range(0, len(references), REFERENCE_BATCH_SIZE):
        batch = references[offset : offset + REFERENCE_BATCH_SIZE]
        filters: list[dict] = [{"terms": {"reference": batch}}]
        if document_type is not None:
            filters.append({"term": {"document_type": document_type}})
        query = {"query": {"bool": {"filter": filters}}}
        async for doc in helpers.async_scan(
            client,
            index=raw_index,
            query=query,
            _source=False,
        ):
            ids.append(doc["_id"])
    return ids


def build_scraper_event(
    *,
    index_suffix: str | None,
    decision_ids: list[str],
    augment: bool,
) -> dict:
    event: dict = {
        "redrive": {
            "complete": False,
            "augment": augment,
            "ids": sorted(decision_ids),
        },
    }
    if index_suffix is not None:
        event["indexSuffix"] = index_suffix
    return event


def warn_if_payload_too_large(payload: str) -> None:
    size = len(payload.encode("utf-8"))
    if size > STEP_FUNCTIONS_INPUT_LIMIT_BYTES:
        print(
            f"Warning: payload is {size:,} bytes; Step Functions execution input "
            f"limit is {STEP_FUNCTIONS_INPUT_LIMIT_BYTES:,} bytes.",
            file=sys.stderr,
        )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a ScraperEvent JSON for pipeline re-indexing."
    )
    parser.add_argument(
        "query",
        help="Elasticsearch query against outcomes-indexed (JSON or query_string)",
    )
    parser.add_argument(
        "--index-suffix",
        default="1012",
        help="Index suffix for outcomes-indexed / outcomes-raw (default: 1012)",
    )
    parser.add_argument(
        "--outcomes-index",
        help="Override outcomes-indexed index name (default: outcomes-indexed-<suffix>)",
    )
    parser.add_argument(
        "--raw-index",
        help="Override outcomes-raw index name (default: outcomes-raw-<suffix>)",
    )
    parser.add_argument(
        "--no-augment",
        action="store_true",
        help="Set redrive.augment=false (passthrough augmenter; index-only refresh)",
    )
    parser.add_argument(
        "--document-type",
        choices=sorted(DocumentType),
        metavar="TYPE",
        help="Only re-index decisions of this type (e.g. method_agreed)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON (default: compact)",
    )
    args = parser.parse_args()

    query = parse_es_query(args.query)
    outcomes_index = args.outcomes_index or index_name(
        "outcomes-indexed", args.index_suffix
    )
    raw_index = args.raw_index or index_name("outcomes-raw", args.index_suffix)

    session = get_boto_session(role_session_name="reindex-outcomes")
    endpoint, auth = get_opensearch_config(session)
    client = create_client(
        cluster_host=endpoint,
        auth=auth,
        async_client=True,
    )

    try:
        print(f"Querying {outcomes_index}…", file=sys.stderr)
        references = await collect_outcome_references(client, outcomes_index, query)
        print(f"Matched {len(references)} outcome(s).", file=sys.stderr)

        if not references:
            print("No outcomes matched; nothing to re-index.", file=sys.stderr)
            sys.exit(1)

        print(f"Resolving raw decision IDs from {raw_index}…", file=sys.stderr)
        if args.document_type:
            print(f"Filtering to document_type={args.document_type}.", file=sys.stderr)
        decision_ids = await collect_raw_decision_ids(
            client,
            raw_index,
            references,
            document_type=args.document_type,
        )
        print(f"Found {len(decision_ids)} raw decision document(s).", file=sys.stderr)

        if not decision_ids:
            print(
                "No raw decision documents found for matched outcomes. "
                "Check --index-suffix / index overrides"
                + (f" / --document-type {args.document_type}." if args.document_type else "."),
                file=sys.stderr,
            )
            sys.exit(1)

        covered_references = {ref.split(":", 1)[0] for ref in decision_ids}
        missing = len(references) - len(covered_references)
        if missing > 0:
            if args.document_type:
                print(
                    f"Warning: {missing} outcome(s) have no "
                    f"{args.document_type} document in {raw_index}.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"Warning: {missing} outcome(s) have no documents in {raw_index}.",
                    file=sys.stderr,
                )

        event = build_scraper_event(
            index_suffix=args.index_suffix,
            decision_ids=decision_ids,
            augment=not args.no_augment,
        )
        payload = json.dumps(
            event, indent=2 if args.pretty else None, separators=(",", ":")
        )
        warn_if_payload_too_large(payload)
        print(payload)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
