import re

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .services.opensearch_connectors import OpensearchSink, OpensearchSource


def get_parties(outcome):
    title = outcome["outcome_title"]
    title = re.sub(r"\s+\(\d+\)$", "", title)  # Remove any trailing ordinal
    union, employer = re.split(r"\s+(?:&|and)\s+", title, maxsplit=1)

    return {
        "union": union,
        "employer": employer
    }


def get_bargaining_unit(data):
    try:
        bu = data["validity_decision"]["bargaining_unit"]
    except KeyError:
        try:
            bu = data["acceptance_decision"]["bargaining_unit"]
        except KeyError:
            return None

    return {
        **bu,
        "membership_pct": pct(bu["membership"], bu["size"]),
        "supporters_pct": pct(bu["supporters"], bu["size"]),
    }


def bargaining_unit_size(bargaining_unit, data):
    try:
        return data["recognition_decision"]["ballot"]["eligible_workers"]
    except (KeyError, TypeError):
        try:
            return bargaining_unit["size"]
        except TypeError:
            return None


def pct(x, n):
    try:
        return 100.0 * x / n
    except TypeError:
        return None


def transform_for_index(outcome):
    data = outcome["extracted_data"]
    parties = get_parties(outcome)
    bargaining_unit = get_bargaining_unit(data)
    try:
        ballot = data["recognition_decision"]["ballot"]
        ballot_details = {
            "ballot_turnout_pct": pct(ballot["votes_in_favor"] + ballot["votes_against"], ballot["eligible_workers"]),
            "ballot_for_pct": pct(ballot["votes_in_favor"], ballot["eligible_workers"]),
        }
    except (KeyError, TypeError):
        ballot_details = {}
    return {
        **outcome,
        "document_types": list(outcome["documents"].keys()),
        "derived_query": {
            "union_name": parties["union"],
            "employer_name": parties["employer"],
            "bargaining_unit_size": bargaining_unit_size(bargaining_unit, data),
            "bargaining_unit": bargaining_unit,
            **ballot_details,
        }
    }


class OutcomeSink(OpensearchSink):
    def id(self, item):
        return item["reference"]


outcomes_source = OpensearchSource(
    cluster_host="http://127.0.0.1",
    cluster_user=None,
    cluster_pass=None,
    index="outcomes-augmented",
    page_size=25,
)
opensearch_sink = OutcomeSink(
    cluster_host="http://127.0.0.1",
    cluster_user=None,
    cluster_pass=None,
    index="outcomes-indexed",
)

flow = Dataflow("final_index_derived")
stream = op.input("outcome_docs", flow, outcomes_source)
docs = op.map("get_doc_source", stream, lambda d: d["_source"])
transformed = op.map("transform_for_index", docs, transform_for_index)
op.output("write", transformed, opensearch_sink)
