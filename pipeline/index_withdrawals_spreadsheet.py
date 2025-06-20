import argparse
import os
from tempfile import NamedTemporaryFile

import bytewax.operators as op
from bytewax.connectors.files import CSVSource
from bytewax.dataflow import Dataflow
from bytewax.testing import run_main

from xlsx2csv import Xlsx2csv

from services.opensearch_connectors import OpensearchSink

parser = argparse.ArgumentParser(
    description="Index application withdrawals from a spreadsheet"
)
parser.add_argument(
    "--infile", type=str, help="Path to the spreadsheet file", required=True
)
args = parser.parse_args()


class WithdrawalSink(OpensearchSink):
    def id(self, item):
        return item["Case Number"]

    def doc(self, item):
        return {
            "reference": item["Case Number"],
            "union": item["Trade Union Name"],
            "employer": item["Employer Name"],
            "application_received": item["Date Application Received"],
            "application_withdrawn": item["Date Application Withdrawn"],
        }


opensearch_sink = WithdrawalSink(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="application-withdrawals-raw",
    mapping_path="pipeline/index_mappings/application_withdrawals.json",
)

flow = Dataflow("index_withdrawals_spreadsheet")

with NamedTemporaryFile(suffix=".csv", delete_on_close=False) as temp_file:
    Xlsx2csv(args.infile, outputencoding="utf-8").convert(temp_file.name)
    withdrawals_source = CSVSource(temp_file.name)

    stream = op.input("withdrawals", flow, withdrawals_source)
    non_empty = op.filter("non_empty", stream, lambda x: bool(x["Case Number"]))
    op.output("index", non_empty, opensearch_sink)
    run_main(flow)
