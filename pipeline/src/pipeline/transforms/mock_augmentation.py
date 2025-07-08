from pipeline.transforms.document_classifier import (
    DocumentType,
    should_get_content,
    should_skip,
)
from polyfactory.factories.pydantic_factory import ModelFactory
from baml_client import types as baml_types


def mock(model):
    return ModelFactory.create_factory(model=model).build().model_dump(by_alias=True)


async def get_extracted_data(doc_type_string, content):
    document_type = DocumentType[doc_type_string]
    if not should_get_content(document_type) or should_skip(document_type):
        return None
    match document_type:
        case DocumentType.acceptance_decision:
            return mock(baml_types.AcceptanceDecision)
        case DocumentType.bargaining_unit_decision:
            return mock(baml_types.BargainingUnitDecision)
        case DocumentType.bargaining_decision:
            return mock(baml_types.BargainingDecision)
        case DocumentType.form_of_ballot_decision:
            return mock(baml_types.FormOfBallotDecision)
        case DocumentType.whether_to_ballot_decision:
            return mock(baml_types.WhetherToBallotDecision)
        case DocumentType.validity_decision:
            return mock(baml_types.ValidityDecision)
        case DocumentType.case_closure:
            return {"decision_date": "2025-01-01"}
        case DocumentType.recognition_decision:
            return mock(baml_types.RecognitionDecision)
        case DocumentType.application_received:
            return {"decision_date": "2025-01-01"}
        case DocumentType.access_decision_or_dispute:
            return mock(baml_types.AccessDecisionOrDispute)
        case DocumentType.method_agreed:
            return {"decision_date": "2025-01-01"}
        case DocumentType.nullification_decision:
            return None
