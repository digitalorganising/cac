from transitions import Machine
from collections import OrderedDict
from datetime import date
from pipeline.document_classifier import DocumentType
from .model import EventType, OutcomeState, Event

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
    [EventType.CaseClosed, OutcomeState.Recognized, OutcomeState.Closed]
]


def is_state_changing(event_type: EventType):
    # Access disputes are effectively stateless
    return event_type is not EventType.AccessDisputed


class EventsBuilder(Machine):
    def __init__(self):
        self.event_list = []
        Machine.__init__(self, **EventsBuilder.get_machine_params())

    @classmethod
    def get_machine_params(cls):
        return {
            "states": [s.value for s in OutcomeState],
            "transitions": [[e.value, a.value, b.value] for e, a, b in transitions],
            "initial": OutcomeState.Initial.value,
            "auto_transitions": False
        }

    def add_event(self, event_type: EventType, event_date: date | str):
        d = date.fromisoformat(event_date)
        if is_state_changing(event_type):
            self.trigger(event_type.value)

        if self.event_list and d < self.event_list[-1].date:
            raise ValueError(f"Event out of order: {d} is before previous event ({self.event_list[-1].date})")

        self.event_list.append(Event(event_type=event_type, date=d))

    def dump_events(self):
        return [e.model_dump() for e in self.event_list]

    def labelled_state(self):
        return OutcomeState(self.state)


def events_from_data(data, fallback_date):
    events = EventsBuilder()
    sorted_data = OrderedDict(
        sorted(data.items(), key=lambda x: x[1]["decision_date"] if x[1] else fallback_date)
    )
    for doc_type, doc in sorted_data.items():
        match doc_type:
            case DocumentType.application_received:
                events.add_event(EventType.ApplicationReceived, doc["decision_date"])
            case DocumentType.acceptance_decision:
                if events.state is OutcomeState.Initial.value:
                    events.add_event(EventType.ApplicationReceived, doc["application_date"])
                if doc["success"]:
                    events.add_event(EventType.ApplicationAccepted, doc["decision_date"])
                else:
                    events.add_event(EventType.ApplicationRejected, doc["decision_date"])
            case DocumentType.application_withdrawn:
                events.add_event(EventType.ApplicationWithdrawn, fallback_date)
            case DocumentType.bargaining_unit_decision:
                events.add_event(EventType.BargainingUnitDecided, doc["decision_date"])
            case DocumentType.bargaining_decision:
                events.add_event(EventType.MethodDecision, doc["decision_date"])
            case DocumentType.form_of_ballot_decision:
                events.add_event(EventType.BallotFormDecided, doc["decision_date"])
            case DocumentType.whether_to_ballot_decision:
                events.add_event(EventType.BallotRequirementDecided, doc["decision_date"])
            case DocumentType.validity_decision:
                if not doc["valid"]:
                    events.add_event(EventType.ApplicationRejected, doc["decision_date"])
            case DocumentType.case_closure:
                events.add_event(EventType.CaseClosed, doc["decision_date"])
            case DocumentType.recognition_decision:
                if doc["ballot"]:
                    events.add_event(EventType.BallotHeld, doc["ballot"]["start_ballot_period"])

                if doc["union_recognized"]:
                    events.add_event(EventType.UnionRecognized, doc["decision_date"])
                else:
                    events.add_event(EventType.UnionNotRecognized, doc["decision_date"])
            case DocumentType.access_decision_or_dispute:
                events.add_event(EventType.AccessDisputed, doc["decision_date"])
            case DocumentType.method_agreed:
                events.add_event(EventType.MethodAgreed, fallback_date)
            case _:
                print("non-event document encountered")
                print(doc)
    return events
