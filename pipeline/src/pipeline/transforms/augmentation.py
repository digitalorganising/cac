import asyncio
import os
from baml_client import b
from tenacity import retry, stop_after_attempt, wait_random_exponential
from .document_classifier import (
    DocumentType,
    should_get_content,
    should_skip,
)
from ..extractors.date_extractor import extract_date


@retry(
    wait=wait_random_exponential(min=1, max=90),
    stop=stop_after_attempt(7),
    reraise=True,
)
async def get_extracted_data(doc_type_string, content):
    document_type = DocumentType[doc_type_string]
    if not should_get_content(document_type) or should_skip(document_type):
        return None
    match document_type:
        case DocumentType.acceptance_decision:
            return await b.ExtractAcceptanceDecision(content).model_dump()
        case DocumentType.bargaining_unit_decision:
            return await b.ExtractBargainingUnitDecision(content).model_dump()
        case DocumentType.bargaining_decision:
            return await b.ExtractBargainingDecision(content).model_dump()
        case DocumentType.form_of_ballot_decision:
            return await b.ExtractFormOfBallotDecision(content).model_dump()
        case DocumentType.whether_to_ballot_decision:
            return await b.ExtractWhetherToBallotDecision(content).model_dump()
        case DocumentType.validity_decision:
            return await b.ExtractValidityDecision(content).model_dump()
        case DocumentType.case_closure:
            return {"decision_date": extract_date(content)}
        case DocumentType.recognition_decision:
            return await b.ExtractRecognitionDecision(content).model_dump()
        case DocumentType.application_received:
            return {"decision_date": extract_date(content)}
        case DocumentType.access_decision_or_dispute:
            return await b.ExtractAccessDecisionOrDispute(content).model_dump()
        case DocumentType.method_agreed:
            return {"decision_date": extract_date(content)}
        case DocumentType.nullification_decision:
            return None


if os.getenv("MOCK_LLM"):
    from .mock_augmentation import get_extracted_data


async def augment_doc(doc):
    decision_documents = doc.pop("documents", {})
    doc["extracted_data"] = {}
    if DocumentType.derecognition_decision.value in decision_documents:
        return

    async def augment_decision_document(doc_type_string, content):
        extracted_data = await get_extracted_data(doc_type_string, content)
        return doc_type_string, extracted_data

    tasks = [augment_decision_document(*item) for item in decision_documents.items()]
    for coro in asyncio.as_completed(tasks):
        doc_type_string, extracted_data = await coro
        doc["extracted_data"][doc_type_string] = extracted_data

    return doc
