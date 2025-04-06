from ..baml_client import b
from ..document_classifier import DocumentType, should_get_content, should_skip
from .date_extractor import extract_date


def get_extracted_data(doc):
    document_type = DocumentType[doc["document_type"]]
    content = doc["content"]
    if not should_get_content(document_type) or should_skip(document_type):
        return None
    match document_type:
        case DocumentType.acceptance_decision:
            return b.ExtractAcceptanceDecision(content).model_dump()
        case DocumentType.bargaining_unit_decision:
            return b.ExtractBargainingUnitDecision(content).model_dump()
        case DocumentType.bargaining_decision:
            return b.ExtractBargainingDecision(content).model_dump()
        case DocumentType.form_of_ballot_decision:
            return b.ExtractFormOfBallotDecision(content).model_dump()
        case DocumentType.whether_to_ballot_decision:
            return b.ExtractWhetherToBallotDecision(content).model_dump()
        case DocumentType.validity_decision:
            return b.ExtractValidityDecision(content).model_dump()
        case DocumentType.case_closure:
            return {"decision_date": extract_date(content)}
        case DocumentType.recognition_decision:
            return b.ExtractRecognitionDecision(content).model_dump()
        case DocumentType.application_received:
            return {"decision_date": extract_date(content)}
        case DocumentType.access_decision_or_dispute:
            return b.ExtractAccessDecisionOrDispute(content).model_dump()
        case DocumentType.method_agreed:
            return {"decision_date": extract_date(content)}
        case DocumentType.nullification_decision:
            return None
