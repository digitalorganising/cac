from transitions import Machine, MachineError
from collections import OrderedDict
from dateutil.parser import parse as date_parse
from typing import Optional

from ..document_classifier import DocumentType
from .model import EventType, OutcomeState, Event
from .known_bad_data import allow_transform_errors

transitions = [
    [EventType.ApplicationReceived, OutcomeState.Initial, OutcomeState.PendingApplicationDecision],
    [EventType.ApplicationWithdrawn, OutcomeState.PendingApplicationDecision, OutcomeState.Withdrawn],
    [EventType.ApplicationAccepted, OutcomeState.PendingApplicationDecision, OutcomeState.PendingRecognitionDecision],
    [EventType.ApplicationRejected, OutcomeState.PendingApplicationDecision, OutcomeState.ApplicationRejected],
    [EventType.ApplicationWithdrawn, OutcomeState.PendingRecognitionDecision, OutcomeState.Withdrawn],
    [EventType.BargainingUnitDecided, OutcomeState.PendingRecognitionDecision, OutcomeState.PendingRecognitionDecision],
    [EventType.BallotRequirementDecided, OutcomeState.PendingRecognitionDecision,
     OutcomeState.PendingRecognitionDecision],
    [EventType.BallotFormDecided, OutcomeState.PendingRecognitionDecision, OutcomeState.PendingRecognitionDecision],
    [EventType.ApplicationRejected, OutcomeState.PendingRecognitionDecision, OutcomeState.ApplicationRejected],
    [EventType.UnionRecognized, OutcomeState.PendingRecognitionDecision, OutcomeState.Recognized],
    [EventType.BallotHeld, OutcomeState.PendingRecognitionDecision, OutcomeState.Balloting],
    [EventType.UnionRecognized, OutcomeState.Balloting, OutcomeState.Recognized],
    [EventType.UnionNotRecognized, OutcomeState.Balloting, OutcomeState.NotRecognised],
    [EventType.MethodDecision, OutcomeState.Recognized, OutcomeState.MethodAgreed],
    [EventType.MethodAgreed, OutcomeState.Recognized, OutcomeState.MethodAgreed],
    [EventType.CaseClosed, OutcomeState.Recognized, OutcomeState.Closed],
    [EventType.CaseClosed, OutcomeState.PendingRecognitionDecision, OutcomeState.Closed]
]


def is_state_changing(event_type: EventType):
    # Access disputes are effectively stateless
    return event_type is not EventType.AccessDisputed


def doc_ordering(fallback_date):
    def _doc_order(kv_tuple):
        doc_type, doc = kv_tuple
        # It's pragmatic to have our own tiebreakers
        tiebreaker = {
            DocumentType.application_received: 1,
            DocumentType.application_withdrawn: 2,
            DocumentType.recognition_decision: 3,
            DocumentType.method_agreed: 4
        }.get(doc_type, 0)
        return (
            date_parse(doc["decision_date"]) if doc and doc["decision_date"] else fallback_date,
            tiebreaker
        )

    return _doc_order


class InvalidEventError(Exception):
    pass


class EventsBuilder(Machine):
    def __init__(self, fallback_date):
        self.event_list = []
        self.fallback_date = fallback_date
        Machine.__init__(self, **EventsBuilder.get_machine_params())

    @classmethod
    def get_machine_params(cls):
        return {
            "states": [s.value for s in OutcomeState],
            "transitions": [[e.value, a.value, b.value] for e, a, b in transitions],
            "initial": OutcomeState.Initial.value,
            "auto_transitions": False
        }

    def add_event(self, event_type: EventType, event_date: Optional[str] = None, description: Optional[str] = None):
        d = date_parse(event_date) if event_date else self.fallback_date
        if is_state_changing(event_type):
            self.trigger(event_type.value)

        prev_event = self.event_list[-1] if self.event_list else None
        if prev_event and \
                is_state_changing(event_type) and \
                is_state_changing(prev_event.type) and \
                d.date() < prev_event.date:
            raise ValueError(f"Event out of order: {event_type.value} is before ({d}) previous "
                             f"event {prev_event.type.value} ({prev_event.date})")

        self.event_list.append(Event(type=event_type, date=d.date(), description=description))

    def dump_events(self):
        return [e.model_dump(exclude_none=True) for e in self.event_list]

    def labelled_state(self):
        return OutcomeState(self.state)


def events_from_outcome(outcome):
    fallback_date = date_parse(outcome["last_updated"][:10])
    data = outcome["extracted_data"]
    ref = outcome["reference"]
    sorted_docs = OrderedDict(
        sorted(data.items(), key=doc_ordering(fallback_date))
    )

    # There seem to be a few cases where the last_updated date is wrong
    last_doc = sorted_docs[next(reversed(sorted_docs))]
    if last_doc and last_doc["decision_date"] and fallback_date < date_parse(last_doc["decision_date"]):
        fallback_date = date_parse(last_doc["decision_date"])
        sorted_docs = OrderedDict(
            sorted(data.items(), key=doc_ordering(fallback_date))
        )

    events = EventsBuilder(fallback_date)

    for doc_type, doc in sorted_docs.items():
        try:
            match doc_type:
                case DocumentType.application_received:
                    events.add_event(EventType.ApplicationReceived, doc["decision_date"])
                case DocumentType.acceptance_decision:
                    if events.labelled_state() is OutcomeState.Initial:
                        events.add_event(EventType.ApplicationReceived, doc["application_date"])

                    bargaining_unit = "Bargaining unit: " + doc["bargaining_unit"]["description"]
                    if doc["success"]:
                        events.add_event(EventType.ApplicationAccepted, doc["decision_date"], bargaining_unit)
                    else:
                        events.add_event(EventType.ApplicationRejected, doc["decision_date"], bargaining_unit)
                case DocumentType.application_withdrawn:
                    # This is a workaround until proper withdrawal data is used
                    if events.labelled_state() is OutcomeState.Initial:
                        events.add_event(EventType.ApplicationReceived)
                    events.add_event(EventType.ApplicationWithdrawn)
                case DocumentType.bargaining_unit_decision:
                    new_bargaining_unit = doc["new_bargaining_unit_description"]
                    events.add_event(EventType.BargainingUnitDecided, doc["decision_date"], new_bargaining_unit)
                case DocumentType.bargaining_decision:
                    events.add_event(EventType.MethodDecision, doc["decision_date"])
                case DocumentType.form_of_ballot_decision:
                    ballot_form = doc["form_of_ballot"]
                    events.add_event(EventType.BallotFormDecided, doc["decision_date"], ballot_form)
                case DocumentType.whether_to_ballot_decision:
                    will_ballot = "Ballot required" if doc["decision_to_ballot"] else "Ballot not required"
                    events.add_event(EventType.BallotRequirementDecided, doc["decision_date"], will_ballot)
                case DocumentType.validity_decision:
                    if not doc["valid"]:
                        events.add_event(EventType.ApplicationRejected, doc["decision_date"])
                case DocumentType.case_closure:
                    events.add_event(EventType.CaseClosed, doc["decision_date"])
                case DocumentType.recognition_decision:
                    if doc["ballot"]:
                        ballot_summary = f"{doc['form_of_ballot']} ballot; " \
                                         f"{doc['ballot']['eligible_workers']} eligible workers."
                        events.add_event(EventType.BallotHeld, doc["ballot"]["start_ballot_period"], ballot_summary)

                    if doc["ballot"]:
                        description = f"{doc['ballot']['votes_in_favor']} votes in favour; " \
                                      f"{doc['ballot']['votes_against']} votes against."
                    else:
                        description = "No ballot held"
                    if doc["union_recognized"]:
                        events.add_event(EventType.UnionRecognized, doc["decision_date"], description)
                    else:
                        events.add_event(EventType.UnionNotRecognized, doc["decision_date"], description)
                case DocumentType.access_decision_or_dispute:
                    if "complainant" in doc["details"]:
                        description = f"Complaint from {doc['details']['complainant']} "
                        if doc["details"]["upheld"]:
                            description += "upheld"
                        else:
                            description += "not upheld"
                    else:
                        description = doc["details"]["description"]
                    events.add_event(EventType.AccessDisputed, doc["decision_date"], description)
                case DocumentType.method_agreed:
                    # These sometimes come after a method decision, in which case we ignore them
                    if events.labelled_state() is not OutcomeState.MethodAgreed:
                        events.add_event(EventType.MethodAgreed, doc["decision_date"])
                case DocumentType.nullification_decision:
                    events.add_event(EventType.ApplicationRejected)
                case _:
                    print(f"Non-event document encountered ({doc_type} for {ref})")
        except (MachineError, ValueError) as e:
            if allow_transform_errors(ref):
                print(f"Allowed error: [{e}] for {ref}")
            else:
                raise InvalidEventError({
                    "root_cause": e,
                    "outcome_reference": ref,
                    "current_events": events.dump_events(),
                })
    return events
