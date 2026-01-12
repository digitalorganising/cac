from typing import Optional, Literal, Union
from datetime import datetime
from pydantic import (
    BaseModel,
    RootModel,
    Field,
    ModelWrapValidatorHandler,
    ValidationError,
    model_validator,
)
from typing import Self

from baml_client import types as baml_types
from .documents import DocumentType


class DecisionRaw(BaseModel):
    id: str
    reference: str
    outcome_url: str
    outcome_title: str
    document_type: DocumentType
    last_updated: Optional[datetime] = None
    document_content: Optional[str] = None
    document_url: Optional[str] = None

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        try:
            return handler(data)
        except ValidationError as e:
            print(
                f"Decision validation failed for {data.get('id', 'unknown')} ({data.get('outcome_url', 'unknown')})"
            )
            raise


decision_raw_mapping = {
    "id": {"type": "keyword"},
    "reference": {"type": "keyword"},
    "last_updated": {"type": "date"},
    "outcome_url": {"type": "keyword"},
    "outcome_title": {"type": "text"},
    "document_type": {"type": "keyword"},
    "document_content": {"type": "text"},
    "document_url": {"type": "keyword"},
}


class DateOnly(BaseModel):
    decision_date: str


class DecisionAugmentedDateOnly(DecisionRaw):
    document_type: Literal[
        DocumentType.case_closure,
        DocumentType.application_received,
    ]
    extracted_data: DateOnly


class DecisionAugmentedMethodAgreed(DecisionRaw):
    document_type: Literal[DocumentType.method_agreed]
    extracted_data: Optional[DateOnly] = None


class DecisionAugmentedApplicationWithdrawn(DecisionRaw):
    document_type: Literal[DocumentType.application_withdrawn]
    extracted_data: Optional[DateOnly] = None


date_only_mapping = {
    "decision_date": {"type": "keyword"},
}


class DecisionAugmentedAcceptance(DecisionRaw):
    document_type: Literal[DocumentType.acceptance_decision]
    extracted_data: baml_types.AcceptanceDecision


bargaining_unit_mapping = {
    "description": {"type": "text"},
    "size": {"type": "integer"},
    "size_considered": {"type": "boolean"},
    "claimed_membership": {"type": "integer"},
    "membership": {"type": "integer"},
    "locations": {"type": "text"},
}


acceptance_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "success": {"type": "boolean"},
    "rejection_reasons": {"type": "keyword"},
    "application_date": {"type": "keyword"},
    "end_of_acceptance_period": {"type": "keyword"},
    "petition_signatures": {"type": "integer"},
    "bargaining_unit": {"properties": bargaining_unit_mapping},
    "bargaining_unit_agreed": {"type": "boolean"},
}


class DecisionAugmentedBargainingUnit(DecisionRaw):
    document_type: Literal[DocumentType.bargaining_unit_decision]
    extracted_data: baml_types.BargainingUnitDecision


bargaining_unit_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "appropriate_unit_differs": {"type": "boolean"},
    "new_bargaining_unit_description": {"type": "text"},
    "lawyer_present": {"type": "boolean"},
}


class DecisionAugmentedBargaining(DecisionRaw):
    document_type: Literal[DocumentType.bargaining_decision]
    extracted_data: baml_types.BargainingDecision


bargaining_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "cac_involvement_date": {"type": "keyword"},
}


class DecisionAugmentedFormOfBallot(DecisionRaw):
    document_type: Literal[DocumentType.form_of_ballot_decision]
    extracted_data: baml_types.FormOfBallotDecision


form_of_ballot_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "form_of_ballot": {"type": "keyword"},
    "employer_preferred": {"type": "keyword"},
    "union_preferred": {"type": "keyword"},
}


class DecisionAugmentedWhetherToBallot(DecisionRaw):
    document_type: Literal[DocumentType.whether_to_ballot_decision]
    extracted_data: baml_types.WhetherToBallotDecision


whether_to_ballot_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "decision_to_ballot": {"type": "boolean"},
    "majority_membership": {"type": "boolean"},
    "qualifying_conditions": {"type": "keyword"},
}


class DecisionAugmentedValidity(DecisionRaw):
    document_type: Literal[DocumentType.validity_decision]
    extracted_data: baml_types.ValidityDecision


validity_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "valid": {"type": "boolean"},
    "rejection_reasons": {"type": "keyword"},
    "new_bargaining_unit": {"properties": bargaining_unit_mapping},
}


class DecisionAugmentedRecognition(DecisionRaw):
    document_type: Literal[DocumentType.recognition_decision]
    extracted_data: baml_types.RecognitionDecision


recognition_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "union_recognized": {"type": "boolean"},
    "form_of_ballot": {"type": "keyword"},
    "ballot": {
        "properties": {
            "eligible_workers": {"type": "integer"},
            "spoiled_ballots": {"type": "integer"},
            "votes_in_favor": {"type": "integer"},
            "votes_against": {"type": "integer"},
            "start_ballot_period": {"type": "keyword"},
            "end_ballot_period": {"type": "keyword"},
        }
    },
    "good_relations_contested": {"type": "boolean"},
}


class DecisionAugmentedAccessDecisionOrDispute(DecisionRaw):
    document_type: Literal[DocumentType.access_decision_or_dispute]
    extracted_data: baml_types.AccessDecisionOrDispute


access_decision_or_dispute_mapping = {
    "decision_date": {"type": "keyword"},
    "details": {
        "properties": {
            "decision_type": {"type": "keyword"},
            "favors": {"type": "keyword"},
            "description": {"type": "text"},
            "upheld": {"type": "boolean"},
            "complainant": {"type": "keyword"},
        }
    },
}


class DecisionAugmentedPara35(DecisionRaw):
    document_type: Literal[DocumentType.para_35_decision]
    extracted_data: baml_types.Para35Decision


para_35_decision_mapping = {
    "decision_date": {"type": "keyword"},
    "application_date": {"type": "keyword"},
    "application_can_proceed": {"type": "boolean"},
}


class DecisionAugmentedNoData(DecisionRaw):
    document_type: Literal[DocumentType.nullification_decision]
    extracted_data: None


class DecisionAugmented(RootModel):
    root: Union[
        DecisionAugmentedAcceptance,
        DecisionAugmentedBargainingUnit,
        DecisionAugmentedBargaining,
        DecisionAugmentedFormOfBallot,
        DecisionAugmentedWhetherToBallot,
        DecisionAugmentedValidity,
        DecisionAugmentedRecognition,
        DecisionAugmentedAccessDecisionOrDispute,
        DecisionAugmentedPara35,
        DecisionAugmentedApplicationWithdrawn,
        DecisionAugmentedMethodAgreed,
        DecisionAugmentedDateOnly,
        DecisionAugmentedNoData,
    ] = Field(discriminator="document_type")

    @classmethod
    def from_raw(cls, raw: DecisionRaw, extracted_data: BaseModel):
        return cls(
            {
                **raw.model_dump(by_alias=True),
                "extracted_data": (
                    extracted_data.model_dump(by_alias=True)
                    if extracted_data is not None
                    else None
                ),
            }
        )


decision_augmented_mapping = {
    **decision_raw_mapping,
    "extracted_data": {
        "properties": {
            **acceptance_decision_mapping,
            **bargaining_unit_decision_mapping,
            **bargaining_decision_mapping,
            **form_of_ballot_decision_mapping,
            **whether_to_ballot_decision_mapping,
            **validity_decision_mapping,
            **recognition_decision_mapping,
            **access_decision_or_dispute_mapping,
            **para_35_decision_mapping,
            **date_only_mapping,
        }
    },
}
