from datetime import datetime
from pydantic import HttpUrl
from plum import dispatch, parametric
from dateutil.parser import parse as date_parse

from ..baml_client import types as baml_types
from ..document_classifier import DocumentType
from .model import Event, EventType


def ensure_period(input: str) -> str:
    if input.endswith("."):
        return input
    return input + "."


@parametric
class Decision:
    def __init__(self, doc: dict, source_url: str, fallback_date: datetime = None):
        self._doc = doc
        self._source_url = source_url
        self._fallback_date = fallback_date

    def doc(self):
        return self._doc

    def source_url(self):
        return self._source_url

    def fallback_date(self):
        return self._fallback_date


@dispatch
def events_from_decision(doc) -> list[Event]:
    return []


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.application_received],
) -> list[Event]:
    application_received = decision.doc()
    return [
        Event(
            type=EventType.ApplicationReceived,
            date=date_parse(application_received["decision_date"]),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.acceptance_decision],
) -> list[Event]:
    acceptance_decision = baml_types.AcceptanceDecision.model_validate(decision.doc())
    bargaining_unit = (
        f"Bargaining unit: {acceptance_decision.bargaining_unit.description}"
    )

    return [
        Event(
            type=EventType.ApplicationReceived,
            date=date_parse(acceptance_decision.application_date),
            source_document_url=decision.source_url(),
        ),
        Event(
            type=(
                EventType.ApplicationAccepted
                if acceptance_decision.success
                else EventType.ApplicationRejected
            ),
            date=date_parse(acceptance_decision.decision_date),
            source_document_url=decision.source_url(),
            description=ensure_period(bargaining_unit),
        ),
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.application_withdrawn],
) -> list[Event]:
    return [
        Event(
            type=EventType.ApplicationReceived,
            date=decision.fallback_date(),
            source_document_url=decision.source_url(),
        ),
        Event(
            type=EventType.ApplicationWithdrawn,
            date=decision.fallback_date(),
            source_document_url=decision.source_url(),
        ),
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.bargaining_unit_decision],
) -> list[Event]:
    bargaining_unit_decision = baml_types.BargainingUnitDecision.model_validate(
        decision.doc()
    )
    if bargaining_unit_decision.appropriate_unit_differs:
        return [
            Event(
                type=EventType.BargainingUnitInappropriate,
                date=date_parse(bargaining_unit_decision.decision_date),
                source_document_url=decision.source_url(),
                description=ensure_period(
                    bargaining_unit_decision.new_bargaining_unit_description
                ),
            )
        ]
    else:
        return [
            Event(
                type=EventType.BargainingUnitAppropriate,
                date=date_parse(bargaining_unit_decision.decision_date),
                source_document_url=decision.source_url(),
                description="The original bargaining unit from the application was determined by the CAC to be appropriate.",
            )
        ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.bargaining_decision],
) -> list[Event]:
    return [
        Event(
            type=EventType.MethodDecision,
            date=date_parse(decision.doc()["decision_date"]),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.form_of_ballot_decision],
) -> list[Event]:
    form_of_ballot_decision = baml_types.FormOfBallotDecision.model_validate(
        decision.doc()
    )
    decision_date = date_parse(form_of_ballot_decision.decision_date)
    ballot_form = form_of_ballot_decision.form_of_ballot
    employer_preferred = str(form_of_ballot_decision.employer_preferred.value).lower()
    union_preferred = str(form_of_ballot_decision.union_preferred.value).lower()
    ballot_form_description = (
        f"Employer preferred {employer_preferred}; union preferred {union_preferred}."
    )
    if ballot_form == baml_types.FormOfBallot.Postal:
        event_type = EventType.BallotFormPostal
    elif ballot_form == baml_types.FormOfBallot.Workplace:
        event_type = EventType.BallotFormWorkplace
    else:
        event_type = EventType.BallotFormCombination
    return [
        Event(
            type=event_type,
            date=decision_date,
            source_document_url=decision.source_url(),
            description=ensure_period(ballot_form_description),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.whether_to_ballot_decision],
) -> list[Event]:
    whether_to_ballot_decision = baml_types.WhetherToBallotDecision.model_validate(
        decision.doc()
    )
    decision_date = date_parse(whether_to_ballot_decision.decision_date)
    if whether_to_ballot_decision.decision_to_ballot:
        qualifying_condition_labels = {
            baml_types.QualifyingCondition.GoodIndustrialRelations: "it being in the interests of good industrial relations",
            baml_types.QualifyingCondition.EvidenceMembersOpposed: "evidence from members of the union that they are opposed to it conducting collective bargaining",
            baml_types.QualifyingCondition.MembershipEvidenceDoubts: "membership evidence that there are doubts about whether members want the union to conduct collective bargaining",
        }
        qualifying_conditions = [
            qualifying_condition_labels[condition]
            for condition in whether_to_ballot_decision.qualifying_conditions
        ]
        description = f"For the reasons of {'; '.join(qualifying_conditions)}."
        return [
            Event(
                type=EventType.BallotRequirementDecided,
                date=decision_date,
                source_document_url=decision.source_url(),
                description=ensure_period(description),
            )
        ]
    else:
        return [
            Event(
                type=EventType.BallotNotRequired,
                date=decision_date,
                source_document_url=decision.source_url(),
                description="There was a majority membership and no other reasons to ballot were identified.",
            )
        ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.validity_decision],
) -> list[Event]:
    validity_decision = baml_types.ValidityDecision.model_validate(decision.doc())
    if not validity_decision.valid:
        return [
            Event(
                type=EventType.ApplicationRejected,
                date=date_parse(validity_decision.decision_date),
                source_document_url=decision.source_url(),
                description="The application was found no longer to be valid after the change of bargaining unit.",
            )
        ]
    else:
        return []


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.case_closure],
) -> list[Event]:
    return [
        Event(
            type=EventType.CaseClosed,
            date=date_parse(decision.doc()["decision_date"]),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.recognition_decision],
) -> list[Event]:
    recognition_decision = baml_types.RecognitionDecision.model_validate(decision.doc())
    events = []
    if recognition_decision.ballot:
        b = recognition_decision.ballot
        ballot_summary = (
            f"{recognition_decision.form_of_ballot.value} ballot with "
            f"{b.eligible_workers} eligible workers "
            f"running from {b.start_ballot_period} to "
            f"{b.end_ballot_period}."
        )
        events.append(
            Event(
                type=EventType.BallotHeld,
                date=date_parse(b.start_ballot_period),
                source_document_url=decision.source_url(),
                description=ensure_period(ballot_summary),
            )
        )

    if recognition_decision.union_recognized:
        events.append(
            Event(
                type=EventType.UnionRecognized,
                date=date_parse(recognition_decision.decision_date),
                source_document_url=decision.source_url(),
                description=(
                    "Workers voted to recognise the union."
                    if recognition_decision.ballot
                    else "No ballot was held."
                ),
            )
        )
    else:
        description = "No ballot was held."
        if recognition_decision.ballot:
            pct_favor = recognition_decision.ballot.votes_in_favor / (
                recognition_decision.ballot.votes_in_favor
                + recognition_decision.ballot.votes_against
            )
            if pct_favor <= 0.5:
                description = "Workers voted against recognition."
            else:
                description = (
                    "Votes in favour fell short of the turnout requirement of 40%."
                )
        events.append(
            Event(
                type=EventType.UnionNotRecognized,
                date=date_parse(recognition_decision.decision_date),
                source_document_url=decision.source_url(),
                description=ensure_period(description),
            )
        )
    return events


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.access_decision_or_dispute],
) -> list[Event]:
    access_decision_or_dispute = baml_types.AccessDecisionOrDispute.model_validate(
        decision.doc()
    )
    if isinstance(
        access_decision_or_dispute.details, baml_types.UnfairPracticeDisputeDecision
    ):
        return [
            Event(
                type=(
                    EventType.UnfairPracticeUpheld
                    if access_decision_or_dispute.details.upheld
                    else EventType.UnfairPracticeNotUpheld
                ),
                date=date_parse(access_decision_or_dispute.decision_date),
                source_document_url=decision.source_url(),
                description=ensure_period(
                    f"Complaint from {str(access_decision_or_dispute.details.complainant.value).lower()}."
                ),
            )
        ]
    else:
        return [
            Event(
                type=EventType.AccessArrangement,
                date=date_parse(access_decision_or_dispute.decision_date),
                source_document_url=decision.source_url(),
                description=ensure_period(
                    access_decision_or_dispute.details.description
                ),
            )
        ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.method_agreed],
) -> list[Event]:
    return [
        Event(
            type=EventType.MethodAgreed,
            date=date_parse(decision.doc()["decision_date"]),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.nullification_decision],
) -> list[Event]:
    return [
        Event(
            type=EventType.ApplicationRejected,
            date=date_parse(decision.doc()["decision_date"]),
            source_document_url=decision.source_url(),
        )
    ]
