import os

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .transforms import (
    get_parties,
    get_bargaining_unit,
    get_key_dates,
    get_ballot_result,
    events_from_outcome,
    flatten_facets,
)
from .services.opensearch_connectors import OpensearchSink, OpensearchSource


def transform_for_index(outcome):
    parties = get_parties(outcome)
    events = events_from_outcome(outcome)
    key_dates = get_key_dates(events)
    bu = get_bargaining_unit(outcome)
    ballot = get_ballot_result(outcome)
    state = events.labelled_state()
    events_json = events.dump_events()
    json_state = {"value": state.value, "label": state.label}

    return {
        "id": outcome["reference"],
        "documents": outcome["documents"],
        "display": {
            "title": outcome["outcome_title"],
            "reference": outcome["reference"],
            "cacUrl": outcome["outcome_url"],
            "lastUpdated": outcome["last_updated"],
            "state": json_state,
            "parties": parties,
            "bargainingUnit": bu,
            "ballot": ballot,
            "events": events_json,
            "keyDates": key_dates,
        },
        "filter": {
            "lastUpdated": outcome["last_updated"],
            "reference": outcome["reference"],
            "state": state.value,
            "parties.unions": parties["unions"],
            "parties.employer": parties["employer"],
            "bargainingUnit.size": bu["size"] if bu else None,
            "events.type": [e["type"]["value"] for e in events_json],
            "events.date": [e["date"] for e in events_json],
            "keyDates.applicationReceived": key_dates["applicationReceived"],
            "keyDates.outcomeConcluded": key_dates["outcomeConcluded"],
        },
        "facet": flatten_facets(
            {
                "state": json_state,
                "parties.unions": parties["unions"],
                "events.type": [e["type"] for e in events_json],
            }
        )
        | {"bargainingUnit.size": bu["size"] if bu else None},
    }


class OutcomeSink(OpensearchSink):
    def id(self, item):
        return item["id"]


outcomes_source = OpensearchSource(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-augmented",
    page_size=25,
)
opensearch_sink = OutcomeSink(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-2025-05-31-indexed",
    mapping_path="pipeline/index_mappings/outcomes_indexed.json",
)

flow = Dataflow("final_index_derived")
stream = op.input("outcome_docs", flow, outcomes_source)
docs = op.map("get_doc_source", stream, lambda d: d["_source"])
transformed = op.map("transform_for_index", docs, transform_for_index)
op.output("write", transformed, opensearch_sink)
