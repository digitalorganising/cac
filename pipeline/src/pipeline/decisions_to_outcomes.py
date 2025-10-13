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


def merge_in_decision(decision, outcome):
    document_type = decision.pop("document_type")
    document_content = decision.pop("document_content", None)
    document_url = decision.pop("document_url", None)
    extracted_data = decision.pop("extracted_data", None)
    reference = decision.pop("reference")
    return {
        **outcome,
        **decision,
        "id": reference,
        "documents": {
            **outcome.get("documents", {}),
            document_type: document_content,
        },
        "document_urls": {
            **outcome.get("document_urls", {}),
            document_type: document_url,
        },
        "extracted_data": {
            **outcome.get("extracted_data", {}),
            document_type: extracted_data,
        },
    }


async def merge_decisions_to_outcomes(
    client, *, indices, non_pipeline_indices, references
):
    # It makes sense to do this all in one function because it relies on the sort
    # order to merge in a simple way.
    res = await client.search(
        index=",".join(indices | non_pipeline_indices),
        body={
            "size": len(references) * len(DocumentType),  # Max possible
            "query": {
                "terms": {"reference": references},
            },
            "sort": [
                {"reference": {"order": "asc"}},
                {"last_updated": {"missing": "_first"}},
                {"document_type": {"order": "asc"}},
            ],
        },
    )

    last_reference = None
    this_outcome = {}

    def get_outcome():
        try:
            validated_outcome = Outcome.model_validate(this_outcome)
            return validated_outcome
        except ValidationError as e:
            if should_allow_validation_error(e):
                print("Incomplete outcome missing last_updated", this_outcome["id"])
            else:
                raise e

    for hit in res["hits"]["hits"]:
        index = hit["_index"]
        decision = hit["_source"]

        if last_reference is None:
            last_reference = decision["reference"]

        if decision["reference"] != last_reference:
            last_reference = decision["reference"]
            outcome = get_outcome()
            if outcome:
                yield outcome, index
            this_outcome = {}

        this_outcome = merge_in_decision(decision, this_outcome)
    if this_outcome:
        outcome = get_outcome()
        if outcome:
            yield outcome, index
