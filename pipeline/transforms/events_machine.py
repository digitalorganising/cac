from transitions import Machine

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
    def __init__(self):
        self.event_list: list[Event] = []
        Machine.__init__(self, **machine_params)

    def add_event(
        self,
        event: Event,
    ):
        prev_event = self.event_list[-1] if self.event_list else None

        if prev_event and event.type == prev_event.type:
            return

        if is_state_changing(event.type):
            self.trigger(event.type.value)

        self.event_list.append(event)

        if (
            prev_event
            and is_state_changing(event.type)
            and is_state_changing(prev_event.type)
            and event.date < prev_event.date
        ):
            raise ValueError(
                f"Event out of order: {event.type.value} is before ({event.date}) previous "
                f"event {prev_event.type.value} ({prev_event.date})"
            )

    def dump_events(self):
        return [e.model_dump(exclude_none=True, by_alias=True) for e in self.event_list]

    def get_event(self, event_type: EventType):
        return next((e for e in self.event_list if e.type == event_type), None)

    def labelled_state(self):
        return OutcomeState(self.state)
