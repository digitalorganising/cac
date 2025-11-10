from datetime import datetime
from plum import dispatch, parametric
from dateutil.parser import parse as date_parse
from typing import Optional, Union

from baml_client import types as baml_types
from ..types.documents import DocumentType
from ..types.outcome import ExtractedData
from .model import Event, EventType


def ensure_period(input: str) -> str:
    if input.endswith("."):
        return input
    return input + "."


@parametric
class Decision:
    def __init__(
        self,
        doc: ExtractedData,
        source_url: Optional[str] = None,
        fallback_date: Optional[datetime] = None,
    ):
        self._doc = doc
        self._source_url = source_url
        self._fallback_date = fallback_date

    def doc(self):
        return self._doc

    def source_url(self):
        return self._source_url

    def decision_date(self):
        doc_date = self.doc().decision_date if self.doc() else None
        return date_parse(doc_date) if doc_date else self._fallback_date


@dispatch
def events_from_decision(doc) -> list[Event]:
    return []


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.para_35_decision],
) -> list[Event]:
    para_35_decision = decision.doc()
    application_received = Event(
        type=EventType.ApplicationReceived,
        date=date_parse(para_35_decision.application_date),
        source_document_url=decision.source_url(),
    )
    if para_35_decision.application_can_proceed:
        return [
            application_received,
            Event(
                type=EventType.ApplicationP35Valid,
                date=date_parse(para_35_decision.decision_date),
                source_document_url=decision.source_url(),
                description="Determined that no other bargaining is in place, and the application can proceed.",
            ),
        ]
    else:
        return [
            application_received,
            Event(
                type=EventType.ApplicationP35Invalid,
                date=date_parse(para_35_decision.decision_date),
                source_document_url=decision.source_url(),
                description="Collective bargaining already in place, application was rejected.",
            ),
        ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.application_received],
) -> list[Event]:
    application_received = decision.doc()
    return [
        Event(
            type=EventType.ApplicationReceived,
            date=date_parse(application_received.decision_date),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.acceptance_decision],
) -> list[Event]:
    acceptance_decision = decision.doc()
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
    events = []
    # TODO: remove this once handling withdrawal state myself
    withdrawals_data_cutoff = date_parse("2025-02-15")
    if decision.decision_date() >= withdrawals_data_cutoff:
        events.append(
            Event(
                type=EventType.ApplicationReceived,
                date=decision.decision_date(),
                source_document_url=decision.source_url(),
            )
        )

    events.append(
        Event(
            type=EventType.ApplicationWithdrawn,
            date=decision.decision_date(),
            source_document_url=decision.source_url(),
        )
    )
    return events


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.bargaining_unit_decision],
) -> list[Event]:
    bargaining_unit_decision = decision.doc()
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
            date=decision.decision_date(),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.form_of_ballot_decision],
) -> list[Event]:
    form_of_ballot_decision = decision.doc()
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
    whether_to_ballot_decision = decision.doc()
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
        if qualifying_conditions:
            description = f"For the reasons of {'; '.join(qualifying_conditions)}."
        elif not whether_to_ballot_decision.majority_membership:
            description = "There was not sufficient evidence of a majority membership."
        else:
            description = "A ballot was decided to not be required."
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
    validity_decision = decision.doc()
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
            date=decision.decision_date(),
            source_document_url=decision.source_url(),
        )
    ]


@dispatch
def events_from_decision(
    decision: Decision[DocumentType.recognition_decision],
) -> list[Event]:
    recognition_decision = decision.doc()
    events = []
    if recognition_decision.ballot:
        b = recognition_decision.ballot
        ballot_summary = (
            f"A {str(recognition_decision.form_of_ballot.value).lower()} ballot with "
            f"{b.eligible_workers} eligible workers "
            f"ran from {b.start_ballot_period} to "
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
    access_decision_or_dispute = decision.doc()
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
            date=decision.decision_date(),
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
            date=decision.decision_date(),
            source_document_url=decision.source_url(),
        )
    ]
