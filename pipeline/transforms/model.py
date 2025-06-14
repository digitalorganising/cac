from datetime import date
from pydantic import BaseModel, field_serializer, HttpUrl, Field
from typing import Optional

from .labelled_enum import LabelledEnum


# These are constructed based on the flowcharts in the CAC annual reports
class EventType(LabelledEnum):
    ApplicationReceived = "application_received", "Application received"
    ApplicationWithdrawn = "application_withdrawn", "Application withdrawn"
    ApplicationAccepted = "application_accepted", "Application accepted"
    ApplicationRejected = "application_rejected", "Application rejected"
    BargainingUnitAppropriate = (
        "bargaining_unit_appropriate",
        "Bargaining unit confirmed",
    )
    BargainingUnitInappropriate = (
        "bargaining_unit_inappropriate",
        "Bargaining unit changed",
    )
    BallotRequirementDecided = (
        "ballot_requirement_decided",
        "Ballot requirement decided",
    )
    BallotFormDecided = "ballot_form_decided", "Form of ballot decided"
    BallotHeld = "ballot_held", "Ballot held"
    AccessDisputed = "access_disputed", "Access disputed"
    UnionRecognized = "union_recognized", "Union recognised"
    UnionNotRecognized = "union_not_recognized", "Union not recognised"
    MethodDecision = "method_decision", "Bargaining method decided"
    MethodAgreed = "method_agreed", "Bargaining method agreed"
    CaseClosed = "case_closed", "Case closed"


# Unlabelled states are hidden
class OutcomeState(LabelledEnum):
    Initial = "initial", None
    Withdrawn = "withdrawn", "Withdrawn"
    PendingApplicationDecision = (
        "pending_application_decision",
        "Pending application decision",
    )
    ApplicationRejected = "application_rejected", "Application rejected"
    PendingRecognitionDecision = (
        "pending_recognition_decision",
        "Pending recognition decision",
    )
    Balloting = "balloting", "Balloting"
    Recognized = "recognized", "Recognised"
    NotRecognized = "not_recognized", "Not recognised"
    MethodAgreed = "method_agreed", "Bargaining method agreed"
    Closed = "closed", "Closed / in liquidation"


class Event(BaseModel):
    type: EventType
    date: date
    description: Optional[str] = None
    source_document_url: HttpUrl = Field(serialization_alias="sourceDocumentUrl")

    @field_serializer("date")
    def serialize_date(self, date: date, _info):
        return date.isoformat()

    @field_serializer("type")
    def serialize_event_type(self, type: EventType, _info):
        return {"value": type.value, "label": type.label}

    @field_serializer("source_document_url")
    def serialize_source_document_url(self, url: HttpUrl, _info):
        return str(url)
