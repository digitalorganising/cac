import re

import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .transforms.events import events_from_outcome, EventsBuilder, EventType, OutcomeState
from .services.opensearch_connectors import OpensearchSink, OpensearchSource
from .baml_client import types as baml_types


def get_parties(outcome):
    title = outcome["outcome_title"]
    title = re.sub(r"\s+\(\d+\)$", "", title)  # Remove any trailing ordinal
    union, employer = re.split(r"\s+(?:&|and)\s+", title, maxsplit=1)

    return {
        "union": union,
        "employer": employer
    }


def get_bargaining_unit(outcome):
    data = outcome["extracted_data"]
    if "validity_decision" in data:
        d = baml_types.ValidityDecision.model_validate(data["validity_decision"])
        return {
            "size": d.new_bargaining_unit.size,
            "membership": d.new_bargaining_unit.membership,
            "description": d.new_bargaining_unit.description
        }

    if "acceptance_decision" in data:
        d = baml_types.AcceptanceDecision.model_validate(data["acceptance_decision"])
        return {
            "size": d.bargaining_unit.size,
            "membership": d.bargaining_unit.membership,
            "description": d.bargaining_unit.description
        }

    return None


def get_key_dates(events: EventsBuilder):
    application_received = events.get_event(EventType.ApplicationReceived)
    concluded = None
    method_agreed = None
    state = events.labelled_state()
    if state in [
        OutcomeState.Withdrawn,
        OutcomeState.Recognized,
        OutcomeState.NotRecognized,
        OutcomeState.ApplicationRejected,
        OutcomeState.Closed
    ]:
        last_event = events.event_list[-1]
        concluded = last_event.date
    elif state == OutcomeState.MethodAgreed:
        recognition = events.get_event(EventType.UnionRecognized)
        concluded = recognition.date
        method_agreed = events.event_list[-1].date

    return {
        "applicationReceived": application_received.date,
        "outcomeConcluded": concluded,
        "methodAgreed": method_agreed,
    }


def get_ballot_result(outcome):
    d = outcome["extracted_data"]
    if "recognition_decision" in d:
        d = baml_types.RecognitionDecision.model_validate(d["recognition_decision"])
        if d.ballot:
            votes = d.ballot.votes_in_favor + d.ballot.votes_against + d.ballot.spoiled_ballots
            return {
                "turnoutPercent": 100 * votes / d.ballot.eligible_workers,
                "eligible": d.ballot.eligible_workers,
                "inFavor": {
                    "n": d.ballot.votes_in_favor,
                    "percentVotes": 100 * d.ballot.votes_in_favor / votes,
                    "percentBU": 100 * d.ballot.votes_in_favor / d.ballot.eligible_workers
                },
                "against": {
                    "n": d.ballot.votes_against,
                    "percentVotes": 100 * d.ballot.votes_against / votes,
                    "percentBU": 100 * d.ballot.votes_against / d.ballot.eligible_workers
                },
                "spoiled": {
                    "n": d.ballot.spoiled_ballots,
                    "percentVotes": 100 * d.ballot.spoiled_ballots / votes,
                    "percentBU": 100 * d.ballot.spoiled_ballots / d.ballot.eligible_workers
                },
            }

    return None


def transform_for_index(outcome):
    parties = get_parties(outcome)
    events = events_from_outcome(outcome)
    key_dates = get_key_dates(events)
    bu = get_bargaining_unit(outcome)
    ballot = get_ballot_result(outcome)
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
            "bargainingUnit": bu,
            "ballot": ballot,
            "events": events.dump_events(),
            "keyDates": key_dates
        },
        "filter": {
            "state": state.value,
            "parties": parties,
            "bargainingUnit": bu,
            "ballot": ballot,
            "keyDates": key_dates
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
