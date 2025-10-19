import asyncio
import os

from ..types.documents import DocumentType
from ..services.baml import authenticated_client, large_client, with_retry_client
from .document_classifier import should_get_content, should_skip
from ..extractors.date_extractor import extract_date
from ..types.decisions import DecisionAugmented, DecisionRaw, DateOnly


@with_retry_client(authenticated_client, large_client)
async def get_extracted_data(doc_type_string, content, *, client):
    document_type = DocumentType[doc_type_string]
    if not should_get_content(document_type) or should_skip(document_type):
        return None
    match document_type:
        case DocumentType.para_35_decision:
            return await client.ExtractPara35Decision(content)
        case DocumentType.acceptance_decision:
            return await client.ExtractAcceptanceDecision(content)
        case DocumentType.bargaining_unit_decision:
            return await client.ExtractBargainingUnitDecision(content)
        case DocumentType.bargaining_decision:
            return await client.ExtractBargainingDecision(content)
        case DocumentType.form_of_ballot_decision:
            return await client.ExtractFormOfBallotDecision(content)
        case DocumentType.whether_to_ballot_decision:
            return await client.ExtractWhetherToBallotDecision(content)
        case DocumentType.validity_decision:
            return await client.ExtractValidityDecision(content)
        case DocumentType.case_closure:
            return DateOnly(decision_date=extract_date(content))
        case DocumentType.recognition_decision:
            return await client.ExtractRecognitionDecision(content)
        case DocumentType.application_received:
            return DateOnly(decision_date=extract_date(content))
        case DocumentType.access_decision_or_dispute:
            return await client.ExtractAccessDecisionOrDispute(content)
        case DocumentType.method_agreed:
            date = extract_date(content)
            if date is None:
                return None
            return DateOnly(decision_date=extract_date(content))
        case DocumentType.nullification_decision:
            return None


if os.getenv("MOCK_LLM"):
    from .mock_augmentation import get_extracted_data


async def augment_doc(doc: DecisionRaw):
    if doc.document_type == DocumentType.derecognition_decision.value:
        return doc

    extracted_data = await get_extracted_data(doc.document_type, doc.document_content)
    model = DecisionAugmented.from_raw(doc, extracted_data)
    return model.model_dump(by_alias=True)
