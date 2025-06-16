from transitions import Machine, MachineError
from collections import OrderedDict
from dateutil.parser import parse as date_parse
from typing import Optional

from ..document_classifier import DocumentType
from .model import EventType, OutcomeState, Event
from .known_bad_data import allow_transform_errors

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


def doc_ordering(fallback_date):
    def _doc_order(kv_tuple):
        doc_type, doc = kv_tuple
        # It's pragmatic to have our own tiebreakers
        tiebreaker = {
            DocumentType.application_received: 1,
            DocumentType.application_withdrawn: 2,
            DocumentType.recognition_decision: 3,
            DocumentType.method_agreed: 4,
        }.get(doc_type, 0)
        return (
            (
                date_parse(doc["decision_date"])
                if doc and doc["decision_date"]
                else fallback_date
            ),
            tiebreaker,
        )

    return _doc_order


class InvalidEventError(Exception):
    pass


class EventsBuilder(Machine):
    def __init__(self, fallback_date, document_urls):
        self.event_list: list[Event] = []
        self.fallback_date = fallback_date
        self.document_urls = document_urls
        Machine.__init__(self, **EventsBuilder.get_machine_params())

    @classmethod
    def get_machine_params(cls):
        return {
            "states": [s.value for s in OutcomeState],
            "transitions": [[e.value, a.value, b.value] for e, a, b in transitions],
            "initial": OutcomeState.Initial.value,
            "auto_transitions": False,
        }

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


def events_from_outcome(outcome):
    fallback_date = date_parse(outcome["last_updated"][:10])
    data = outcome["extracted_data"]
    ref = outcome["reference"]
    sorted_docs = OrderedDict(sorted(data.items(), key=doc_ordering(fallback_date)))
    document_urls = outcome["document_urls"]

    # Escape hatch below: this only happens where there is a previous application receipt
    # but now the application has been withdrawn.
    if (
        "application_received" in document_urls
        and "application_withdrawn" in document_urls
        and document_urls["application_received"] is None
    ):
        document_urls["application_received"] = document_urls["application_withdrawn"]

    # There seem to be a few cases where the last_updated date is wrong
    last_doc = sorted_docs[next(reversed(sorted_docs))]
    if (
        last_doc
        and last_doc["decision_date"]
        and fallback_date < date_parse(last_doc["decision_date"])
    ):
        fallback_date = date_parse(last_doc["decision_date"])
        sorted_docs = OrderedDict(sorted(data.items(), key=doc_ordering(fallback_date)))

    events = EventsBuilder(fallback_date, document_urls)

    for doc_type, doc in sorted_docs.items():
        try:
            match doc_type:
                case DocumentType.application_received:
                    if events.labelled_state() is OutcomeState.Initial:
                        events.add_event(
                            EventType.ApplicationReceived,
                            doc_type,
                            doc["decision_date"],
                        )
                case DocumentType.acceptance_decision:
                    if events.labelled_state() is OutcomeState.Initial:
                        events.add_event(
                            EventType.ApplicationReceived,
                            doc_type,
                            doc["application_date"],
                        )

                    bargaining_unit = (
                        "Bargaining unit: " + doc["bargaining_unit"]["description"]
                    )
                    if doc["success"]:
                        events.add_event(
                            EventType.ApplicationAccepted,
                            doc_type,
                            doc["decision_date"],
                            bargaining_unit,
                        )
                    else:
                        events.add_event(
                            EventType.ApplicationRejected,
                            doc_type,
                            doc["decision_date"],
                            bargaining_unit,
                        )
                case DocumentType.application_withdrawn:
                    # This is a workaround until proper withdrawal data is used
                    if events.labelled_state() is OutcomeState.Initial:
                        events.add_event(EventType.ApplicationReceived, doc_type)
                    events.add_event(EventType.ApplicationWithdrawn, doc_type)
                case DocumentType.bargaining_unit_decision:
                    if doc["appropriate_unit_differs"]:
                        events.add_event(
                            EventType.BargainingUnitInappropriate,
                            doc_type,
                            doc["decision_date"],
                            doc["new_bargaining_unit_description"],
                        )
                    else:
                        events.add_event(
                            EventType.BargainingUnitAppropriate,
                            doc_type,
                            doc["decision_date"],
                            "The original bargaining unit from the application was determined by the CAC to be appropriate.",
                        )
                case DocumentType.bargaining_decision:
                    events.add_event(
                        EventType.MethodDecision, doc_type, doc["decision_date"]
                    )
                case DocumentType.form_of_ballot_decision:
                    ballot_form = doc["form_of_ballot"]
                    employer_preferred = doc["employer_preferred"]
                    union_preferred = doc["union_preferred"]
                    ballot_form_description = f"Employer preferred: {employer_preferred}; Union preferred: {union_preferred}"
                    if ballot_form == "Postal":
                        events.add_event(
                            EventType.BallotFormPostal,
                            doc_type,
                            doc["decision_date"],
                            ballot_form_description,
                        )
                    elif ballot_form == "Workplace":
                        events.add_event(
                            EventType.BallotFormWorkplace,
                            doc_type,
                            doc["decision_date"],
                            ballot_form_description,
                        )
                    elif ballot_form == "Combination":
                        events.add_event(
                            EventType.BallotFormCombination,
                            doc_type,
                            doc["decision_date"],
                            ballot_form_description,
                        )
                case DocumentType.whether_to_ballot_decision:
                    if doc["decision_to_ballot"]:
                        qualifying_condition_labels = {
                            "GoodIndustrialRelations": "it being in the interests of good industrial relations",
                            "EvidenceMembersOpposed": "evidence from members of the union that they are opposed to it conducting collective bargaining",
                            "MembershipEvidenceDoubts": "membership evidence that there are doubts about whether members want the union to conduct collective bargaining",
                        }
                        qualifying_conditions = [
                            qualifying_condition_labels[condition]
                            for condition in doc["qualifying_conditions"]
                        ]
                        if not doc["majority_membership"] or not qualifying_conditions:
                            description = "No evidence of majority membership."
                        else:
                            description = f"For the reasons of {'; '.join(qualifying_conditions)}."
                        events.add_event(
                            EventType.BallotRequirementDecided,
                            doc_type,
                            doc["decision_date"],
                            description,
                        )
                    else:
                        events.add_event(
                            EventType.BallotNotRequired,
                            doc_type,
                            doc["decision_date"],
                            "There was a majority membership and no other reasons to ballot",
                        )
                case DocumentType.validity_decision:
                    if not doc["valid"]:
                        events.add_event(
                            EventType.ApplicationRejected,
                            doc_type,
                            doc["decision_date"],
                        )
                case DocumentType.case_closure:
                    events.add_event(
                        EventType.CaseClosed, doc_type, doc["decision_date"]
                    )
                case DocumentType.recognition_decision:
                    if doc["ballot"]:
                        ballot_summary = (
                            f"{doc['form_of_ballot']} ballot with "
                            f"{doc['ballot']['eligible_workers']} eligible workers "
                            f"running from {doc['ballot']['start_ballot_period']} to "
                            f"{doc['ballot']['end_ballot_period']}."
                        )
                        events.add_event(
                            EventType.BallotHeld,
                            doc_type,
                            doc["ballot"]["start_ballot_period"],
                            ballot_summary,
                        )

                    if doc["union_recognized"]:
                        events.add_event(
                            EventType.UnionRecognized,
                            doc_type,
                            doc["decision_date"],
                            (
                                "Workers voted to recognise the union."
                                if doc["ballot"]
                                else "No ballot held."
                            ),
                        )
                    else:
                        description = "No ballot held."
                        if doc["ballot"]:
                            pct_favor = doc["ballot"]["votes_in_favor"] / (
                                doc["ballot"]["votes_in_favor"]
                                + doc["ballot"]["votes_against"]
                            )
                            if pct_favor <= 0.5:
                                description = "Workers voted against recognition."
                            else:
                                description = "Votes in favour fell short of the turnout requirement of 40%."
                        events.add_event(
                            EventType.UnionNotRecognized,
                            doc_type,
                            doc["decision_date"],
                            description,
                        )
                case DocumentType.access_decision_or_dispute:
                    if "upheld" in doc["details"]:
                        description = f"Complaint from {doc['details']['complainant']} "
                        if doc["details"]["upheld"]:
                            events.add_event(
                                EventType.UnfairPracticeUpheld,
                                doc_type,
                                doc["decision_date"],
                                description,
                            )
                        else:
                            events.add_event(
                                EventType.UnfairPracticeNotUpheld,
                                doc_type,
                                doc["decision_date"],
                                description,
                            )
                    else:
                        events.add_event(
                            EventType.AccessArrangement,
                            doc_type,
                            doc["decision_date"],
                            doc["details"]["description"],
                        )
                case DocumentType.method_agreed:
                    # These sometimes come after a method decision, in which case we ignore them
                    if events.labelled_state() is not OutcomeState.MethodAgreed:
                        events.add_event(
                            EventType.MethodAgreed, doc_type, doc["decision_date"]
                        )
                case DocumentType.nullification_decision:
                    events.add_event(EventType.ApplicationRejected, doc_type)
                case _:
                    print(f"Non-event document encountered ({doc_type} for {ref})")
        except (MachineError, ValueError) as e:
            if allow_transform_errors(ref):
                print(f"Allowed error: [{e}] for {ref}")
            else:
                raise InvalidEventError(
                    {
                        "root_cause": e,
                        "outcome_reference": ref,
                        "current_events": events.dump_events(),
                    }
                )
    return events
