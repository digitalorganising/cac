import argparse
import asyncio
import csv
import os
from tempfile import NamedTemporaryFile

from opensearchpy import helpers
from tqdm.asyncio import tqdm
from xlsx2csv import Xlsx2csv

from pipeline.services.opensearch_utils import (
    create_client,
    get_auth,
    ensure_index_mapping,
)
from pipeline import london_date
from pipeline.transforms import normalize_reference
from pipeline.transforms.document_classifier import DocumentType
from pipeline.types.decisions import decision_augmented_mapping

parser = argparse.ArgumentParser(
    description="Index application withdrawals from a spreadsheet"
)
parser.add_argument(
    "--infile", type=str, help="Path to the spreadsheet file", required=True
)
parser.add_argument(
    "--index", type=str, help="OpenSearch index to write to", required=True
)
parser.add_argument(
    "--reference-url",
    type=str,
    help="URL to use for these decisions",
    required=True,
)
args = parser.parse_args()


def try_london_date(date_str):
    try:
        return london_date(date_str)
    except ValueError:
        return None


def withdrawal_to_docs(withdrawal, reference_url):
    normalized_reference = normalize_reference(withdrawal["Case Number"])
    application_received = try_london_date(withdrawal["Date Application Received"])
    application_withdrawn = try_london_date(withdrawal["Date Application Withdrawn"])
    union = withdrawal["Trade Union Name"]
    employer = withdrawal["Employer Name"]

    common = {
        "reference": normalized_reference,
        "document_url": reference_url,
    }

    if application_received:
        yield {
            **common,
            "id": normalized_reference + ":" + DocumentType.application_received.value,
            "document_type": DocumentType.application_received,
            "document_content": f"Application to {employer} from {union} received on {application_received.isoformat()}.",
            "extracted_data": {
                "decision_date": application_received.strftime("%Y-%m-%d"),
            },
        }

    if application_withdrawn:
        yield {
            **common,
            "id": normalized_reference + ":" + DocumentType.application_withdrawn.value,
            "last_updated": application_withdrawn.isoformat(),
            "document_type": DocumentType.application_withdrawn,
            "document_content": f"Application to {employer} withdrawn by {union} on {application_withdrawn.isoformat()}.",
            "extracted_data": {
                "decision_date": application_withdrawn.strftime("%Y-%m-%d"),
            },
        }


def withdrawals_to_actions(withdrawals, index, reference_url):
    for withdrawal in withdrawals:
        if not withdrawal["Case Number"]:
            continue
        for doc in withdrawal_to_docs(withdrawal, reference_url):
            yield {
                "_id": doc["id"],
                "_index": index,
                "_op_type": "update",
                "doc_as_upsert": True,
                "doc": doc,
            }


client = create_client(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    auth=get_auth(credentials_secret=os.getenv("OPENSEARCH_CREDENTIALS_SECRET")),
    async_client=True,
)


async def index_withdrawals(infile, index, reference_url):
    await ensure_index_mapping(
        client, index, {"dynamic": "strict", "properties": decision_augmented_mapping}
    )

    with NamedTemporaryFile(
        suffix=".csv", mode="w+t", encoding="utf-8", delete_on_close=False
    ) as temp_file:
        Xlsx2csv(infile, outputencoding="utf-8").convert(temp_file.name)
        withdrawals = csv.DictReader(temp_file)
        index_actions = withdrawals_to_actions(withdrawals, index, reference_url)
        async for _ in tqdm(
            helpers.async_streaming_bulk(
                client,
                index_actions,
            )
        ):
            pass

    await client.close()


if __name__ == "__main__":
    asyncio.run(index_withdrawals(args.infile, args.index, args.reference_url))
