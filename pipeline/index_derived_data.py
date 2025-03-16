import re

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .transforms.events import events_from_outcome
from .services.opensearch_connectors import OpensearchSink, OpensearchSource


def get_parties(outcome):
    title = outcome["outcome_title"]
    title = re.sub(r"\s+\(\d+\)$", "", title)  # Remove any trailing ordinal
    union, employer = re.split(r"\s+(?:&|and)\s+", title, maxsplit=1)

    return {
        "union": union,
        "employer": employer
    }


def transform_for_index(outcome):
    parties = get_parties(outcome)
    events = events_from_outcome(outcome)
    state = events.labelled_state()
    json_state = {
        "value": state.value,
        "label": state.label
    }

    return {
        **outcome,
        "display": {
            "title": outcome["outcome_title"],
            "reference": outcome["reference"],
            "cacUrl": outcome["outcome_url"],
            "lastUpdated": outcome["last_updated"],
            "state": json_state,
            "parties": parties,
            "events": events.dump_events()
        },
        "filter": {
            "state": state.value,
            "parties": parties
        },
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
