import json
import re

from pydantic import ValidationError
from baml_client import types as baml_types

from .events import EventsBuilder, EventType, OutcomeState, events_from_outcome
from .known_bad_data import override_reference


def normalize_reference(raw_reference):
    reference = override_reference(raw_reference)
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


def get_parties(outcome):
    title = outcome["outcome_title"]
    title = re.sub(r"\s+\(\d+\)$", "", title)  # Remove any trailing ordinal
    union, employer = re.split(r"\s+(?:&|and)\s+", title, maxsplit=1)

    return {"unions": union.split(", "), "employer": employer}


def get_bargaining_unit(outcome):
    data = outcome["extracted_data"]
    if "validity_decision" in data:
        d = baml_types.ValidityDecision.model_validate(data["validity_decision"])
        return {
            "size": (
                d.new_bargaining_unit.size
                if d.new_bargaining_unit.size_considered
                else None
            ),
            "membership": d.new_bargaining_unit.membership
            or d.new_bargaining_unit.claimed_membership,
            "description": d.new_bargaining_unit.description,
            "petitionSignatures": d.petition_signatures,
        }

    if "acceptance_decision" in data:
        d = baml_types.AcceptanceDecision.model_validate(data["acceptance_decision"])
        return {
            "size": (
                d.bargaining_unit.size if d.bargaining_unit.size_considered else None
            ),
            "membership": d.bargaining_unit.membership
            or d.bargaining_unit.claimed_membership,
            "description": d.bargaining_unit.description,
            "petitionSignatures": d.petition_signatures,
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
        OutcomeState.Closed,
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
            votes = (
                d.ballot.votes_in_favor
                + d.ballot.votes_against
                + d.ballot.spoiled_ballots
            )
            return {
                "turnoutPercent": 100 * votes / d.ballot.eligible_workers,
                "eligible": d.ballot.eligible_workers,
                "inFavor": {
                    "n": d.ballot.votes_in_favor,
                    "percentVotes": 100 * d.ballot.votes_in_favor / votes,
                    "percentBU": 100
                    * d.ballot.votes_in_favor
                    / d.ballot.eligible_workers,
                },
                "against": {
                    "n": d.ballot.votes_against,
                    "percentVotes": 100 * d.ballot.votes_against / votes,
                    "percentBU": 100
                    * d.ballot.votes_against
                    / d.ballot.eligible_workers,
                },
                "spoiled": {
                    "n": d.ballot.spoiled_ballots,
                    "percentVotes": 100 * d.ballot.spoiled_ballots / votes,
                    "percentBU": 100
                    * d.ballot.spoiled_ballots
                    / d.ballot.eligible_workers,
                },
            }

    return None


def flatten_facets(facets):
    def flatten(obj):
        if obj is None:
            return None
        return json.dumps(obj, separators=(",", ":"))

    flat = {}
    for k, v in facets.items():
        if isinstance(v, list):
            flat[k] = [flatten(i) for i in v]
        else:
            flat[k] = flatten(v)

    return flat


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
