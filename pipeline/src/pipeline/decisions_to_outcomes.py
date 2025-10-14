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


def create_merger(non_pipeline_indices):
    accumulator = {}
    index = None

    def _merge(decision, this_index):
        nonlocal accumulator
        nonlocal index
        index = this_index if this_index not in non_pipeline_indices else index
        accumulator = merge_decisions(accumulator, decision)
        return accumulator, index

    return _merge


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

    hits = res["hits"]["hits"]
    last_reference = hits[0]["_source"]["reference"] if hits else None
    do_merge = create_merger(non_pipeline_indices)

    def flush(maybe_outcome):
        try:
            validated_outcome = Outcome.model_validate(maybe_outcome)
            return validated_outcome
        except ValidationError as e:
            if should_allow_validation_error(e):
                print(
                    "Incomplete outcome missing last_updated",
                    this_outcome.get("id", "unknown"),
                )
            else:
                raise e

    for hit in hits:
        index = hit["_index"]
        decision = hit["_source"]

        if decision["reference"] != last_reference:
            last_reference = decision["reference"]
            do_merge = create_merger(non_pipeline_indices)

            outcome = flush(this_outcome)
            if outcome:
                yield outcome, canonical_index

        this_outcome, canonical_index = do_merge(decision, index)

    if hits:
        outcome = flush(this_outcome)
        if outcome:
            yield outcome, canonical_index
