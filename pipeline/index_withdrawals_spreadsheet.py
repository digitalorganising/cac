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
from pipeline.transforms import normalize_reference

parser = argparse.ArgumentParser(
    description="Index application withdrawals from a spreadsheet"
)
parser.add_argument(
    "--infile", type=str, help="Path to the spreadsheet file", required=True
)
parser.add_argument(
    "--index", type=str, help="OpenSearch index to write to", required=True
)
args = parser.parse_args()


def withdrawals_to_actions(withdrawals, index):
    for withdrawal in withdrawals:
        if not withdrawal["Case Number"]:
            continue
        reference = normalize_reference(withdrawal["Case Number"])
        yield {
            "_id": reference,
            "_index": index,
            "_op_type": "update",
            "doc_as_upsert": True,
            "doc": {
                "reference": reference,
                "union": withdrawal["Trade Union Name"],
                "employer": withdrawal["Employer Name"],
                "application_received": withdrawal["Date Application Received"],
                "application_withdrawn": withdrawal["Date Application Withdrawn"],
            },
        }


client = create_client(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    auth=get_auth(),
    async_client=True,
)


async def index_withdrawals(infile, index):
    await ensure_index_mapping(
        client, index, "./index_mappings/application_withdrawals.json"
    )

    with NamedTemporaryFile(
        suffix=".csv", mode="w+t", encoding="utf-8", delete_on_close=False
    ) as temp_file:
        Xlsx2csv(infile, outputencoding="utf-8").convert(temp_file.name)
        withdrawals = csv.DictReader(temp_file)
        index_actions = withdrawals_to_actions(withdrawals, index)
        async for _ in tqdm(
            helpers.async_streaming_bulk(
                client,
                index_actions,
            )
        ):
            pass

    await client.close()


if __name__ == "__main__":
    asyncio.run(index_withdrawals(args.infile, args.index))
