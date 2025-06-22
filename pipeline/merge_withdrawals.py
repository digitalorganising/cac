import os
import re
from dateutil.parser import parse as date_parse

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .services.opensearch_connectors import OpensearchSource, OpensearchSink
from .transforms.known_bad_data import override_reference


def merge_withdrawals(keyed_stream_value):
    key, stream_value = keyed_stream_value
    outcome, withdrawal = stream_value
    if not outcome:
        return None

    if not withdrawal:
        return outcome

    withdrawal_date = date_parse(
        withdrawal["application_withdrawn"], dayfirst=True  # God save the Queen
    )
    outcome["extracted_data"]["application_withdrawn"] = {
        "decision_date": withdrawal_date.isoformat()[:10],
    }

    if (
        "application_received" not in outcome["extracted_data"]
        and "acceptance_decision" not in outcome["extracted_data"]
    ):
        application_received_date = date_parse(
            withdrawal["application_received"], dayfirst=True
        )
        outcome["extracted_data"]["application_received"] = {
            "decision_date": application_received_date.isoformat()[:10],
        }

    return outcome


class OutcomeSink(OpensearchSink):
    def id(self, item):
        return item["reference"]


outcomes_source = OpensearchSource(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-augmented-15062025",
    page_size=25,
)
withdrawals_source = OpensearchSource(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="application-withdrawals-raw",
    page_size=25,
)
opensearch_sink = OutcomeSink(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-merged",
    mapping_path="pipeline/index_mappings/outcomes_augmented.json",
)

flow = Dataflow("final_index_derived")


def outcome_reference_key(d):
    reference = override_reference(d["reference"])
    # Extract the number after TUR1/ and everything after it
    match = re.search(r"TUR1\/(\d+)(.+)", reference)
    if match:
        ref_no = match.group(1)
        suffix = match.group(2)
        # Zero-pad to 4 digits if less than 4 digits
        padded_ref_no = ref_no.zfill(4)
        # Reconstruct the reference with the zero-padded number
        return f"TUR1/{padded_ref_no}{suffix}"
    return reference


outcomes_stream = op.input("outcome_docs", flow, outcomes_source)
outcomes_docs = op.map("outcomes_source", outcomes_stream, lambda d: d["_source"])
keyed_outcomes = op.key_on("keyed_outcomes", outcomes_docs, outcome_reference_key)

withdrawals_stream = op.input("withdrawals", flow, withdrawals_source)
withdrawals_docs = op.map(
    "withdrawals_source", withdrawals_stream, lambda d: d["_source"]
)
keyed_withdrawals = op.key_on(
    "keyed_withdrawals", withdrawals_docs, outcome_reference_key
)

joined_stream = op.join(
    "joined",
    keyed_outcomes,
    keyed_withdrawals,
    emit_mode="running",
    insert_mode="product",
)
merged_stream = op.filter_map("merge_withdrawals", joined_stream, merge_withdrawals)

op.output("write", merged_stream, opensearch_sink)
