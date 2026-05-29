from company_disambiguator.model import (
    DisambiguatedCompany,
    DisambiguateCompanyRequest,
    request_to_doc_id,
)
from pipeline.transforms import get_parties
from pipeline.types.outcome import Outcome
from .types.documents import DocumentType
from pydantic import ValidationError


def should_allow_validation_error(e: ValidationError) -> bool:
    """
    Determine if a ValidationError should be allowed (not raised).
    Only allows errors related to missing or None last_updated field.
    """
    for error in e.errors():
        # Check if the error is on the last_updated field
        if error["loc"] and error["loc"][0] == "last_updated":
            error_type = error["type"]
            # Allow missing field or datetime_type error with None input
            if error_type in ["missing", "datetime_type"]:
                # For datetime_type, also check if input is None
                if error_type == "datetime_type" and error.get("input") is None:
                    return True
                elif error_type == "missing":
                    return True
    return False


def merge_without_none(dict1: dict, dict2: dict) -> dict:
    return {
        k: dict2.get(k) if dict2.get(k) is not None else dict1.get(k)
        for k in dict1.keys() | dict2.keys()
    }


def merge_decisions(accumulator, decision):
    document_type = decision.pop("document_type")
    document_content = decision.pop("document_content", None)
    document_url = decision.pop("document_url", None)
    extracted_data = decision.pop("extracted_data", None)
    reference = decision.pop("reference")
    assert reference == accumulator.get("reference", reference)
    return {
        **merge_without_none(accumulator, decision),
        "id": reference,
        "documents": {
            **accumulator.get("documents", {}),
            document_type: document_content,
        },
        "document_urls": {
            **accumulator.get("document_urls", {}),
            document_type: document_url,
        },
        "extracted_data": {
            **accumulator.get("extracted_data", {}),
            document_type: extracted_data,
        },
    }


async def merge_decisions_to_outcome(client, *, index, non_pipeline_indices, reference):
    # It makes sense to do this all in one function because it relies on the sort
    # order to merge in a simple way.
    index_names = sorted({index} | set(non_pipeline_indices))
    res = await client.search(
        index=",".join(index_names),
        body={
            "size": len(DocumentType),  # Max possible
            "query": {
                "term": {"reference": reference},
            },
            "sort": [
                {"reference": {"order": "asc"}},
                {"last_updated": {"missing": "_first"}},
                {"document_type": {"order": "asc"}},
            ],
        },
    )

    hits = res["hits"]["hits"]
    maybe_outcome = {"entities": {"company": None}}

    for hit in hits:
        index = hit["_index"]
        decision = hit["_source"]

        if decision.get("document_type") == DocumentType.acceptance_decision.value:
            parties = get_parties(decision.get("outcome_title"))
            extracted_data = decision.get("extracted_data", {})
            bargaining_unit = extracted_data.get("bargaining_unit", {})
            disambiguate_company_request = DisambiguateCompanyRequest(
                name=parties.get("employer"),
                unions=parties.get("unions"),
                application_date=extracted_data.get("decision_date"),
                bargaining_unit=bargaining_unit.get("description"),
                locations=bargaining_unit.get("locations", None),
            )
            company_id = request_to_doc_id(disambiguate_company_request)
            company = await client.get(index="disambiguated-companies", id=company_id)
            company = DisambiguatedCompany.model_validate(
                company["_source"]["disambiguated_company"]
            )
            maybe_outcome["entities"]["company"] = company

        maybe_outcome = merge_decisions(maybe_outcome, decision)

    try:
        validated_outcome = Outcome.model_validate(maybe_outcome)
        return validated_outcome
    except ValidationError as e:
        if should_allow_validation_error(e):
            print(
                "Incomplete outcome missing last_updated",
                maybe_outcome.get("id", "unknown"),
            )
            return None
        raise
