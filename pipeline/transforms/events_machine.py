from transitions import Machine
from dateutil.parser import parse as date_parse
from typing import Optional

from .model import EventType, OutcomeState, Event

transitions = [
    [
        EventType.ApplicationReceived,
        OutcomeState.Initial,
        OutcomeState.PendingApplicationDecision,
    ],
    [
        EventType.ApplicationWithdrawn,
        OutcomeState.PendingApplicationDecision,
        OutcomeState.Withdrawn,
    ],
    [
        EventType.ApplicationAccepted,
        OutcomeState.PendingApplicationDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.ApplicationRejected,
        OutcomeState.PendingApplicationDecision,
        OutcomeState.ApplicationRejected,
    ],
    [
        EventType.ApplicationWithdrawn,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.Withdrawn,
    ],
    [
        EventType.BargainingUnitAppropriate,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BargainingUnitInappropriate,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BallotRequirementDecided,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BallotNotRequired,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BallotFormPostal,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BallotFormWorkplace,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.BallotFormCombination,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.PendingRecognitionDecision,
    ],
    [
        EventType.ApplicationRejected,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.ApplicationRejected,
    ],
    [
        EventType.UnionRecognized,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.Recognized,
    ],
    [
        EventType.BallotHeld,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.Balloting,
    ],
    [EventType.UnionRecognized, OutcomeState.Balloting, OutcomeState.Recognized],
    [EventType.UnionNotRecognized, OutcomeState.Balloting, OutcomeState.NotRecognized],
    [EventType.MethodDecision, OutcomeState.Recognized, OutcomeState.MethodAgreed],
    [EventType.MethodAgreed, OutcomeState.Recognized, OutcomeState.MethodAgreed],
    [EventType.CaseClosed, OutcomeState.Recognized, OutcomeState.Closed],
    [
        EventType.CaseClosed,
        OutcomeState.PendingRecognitionDecision,
        OutcomeState.Closed,
    ],
]


def is_state_changing(event_type: EventType):
    # Access disputes are effectively stateless
    return (
        event_type is not EventType.AccessArrangement
        and event_type is not EventType.UnfairPracticeUpheld
        and event_type is not EventType.UnfairPracticeNotUpheld
    )


machine_params = {
    "states": [s.value for s in OutcomeState],
    "transitions": [[e.value, a.value, b.value] for e, a, b in transitions],
    "initial": OutcomeState.Initial.value,
    "auto_transitions": False,
}


class InvalidEventError(Exception):
    pass


class EventsBuilder(Machine):
    def __init__(self, fallback_date, document_urls):
        self.event_list: list[Event] = []
        self.fallback_date = fallback_date
        self.document_urls = document_urls
        Machine.__init__(self, **machine_params)

    def add_event(
        self,
        event_type: EventType,
        source_document_type: DocumentType,
        event_date: Optional[str] = None,
        description: Optional[str] = None,
    ):
        d = date_parse(event_date) if event_date else self.fallback_date
        if is_state_changing(event_type):
            self.trigger(event_type.value)

        prev_event = self.event_list[-1] if self.event_list else None
        source_document_url = self.document_urls.get(source_document_type)
        self.event_list.append(
            Event(
                type=event_type,
                date=d.date(),
                description=description,
                source_document_url=source_document_url,
            )
        )
        if (
            prev_event
            and is_state_changing(event_type)
            and is_state_changing(prev_event.type)
            and d.date() < prev_event.date
        ):
            raise ValueError(
                f"Event out of order: {event_type.value} is before ({d}) previous "
                f"event {prev_event.type.value} ({prev_event.date})"
            )

    def dump_events(self):
        return [e.model_dump(exclude_none=True, by_alias=True) for e in self.event_list]

    def get_event(self, event_type: EventType):
        return next((e for e in self.event_list if e.type == event_type), None)

    def labelled_state(self):
        return OutcomeState(self.state)
