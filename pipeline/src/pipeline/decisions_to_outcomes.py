from pipeline.types.outcome import Outcome
from .types.documents import DocumentType


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
                {"document_type": {"order": "asc"}},
                {"last_updated": {"missing": "_first"}},
            ],
        },
    )

    last_reference = None
    this_outcome = {}
    outcome_indices = set()
    print(res)

    def get_outcome():
        outcome_index = outcome_indices - non_pipeline_indices
        if len(outcome_index) == 1:
            return Outcome.model_validate(this_outcome), outcome_index.pop()
        else:
            raise ValueError(
                f"Multiple outcome indices found for {this_outcome['id']}: {outcome_indices}"
            )

    for hit in res["hits"]["hits"]:
        index = hit["_index"]
        decision = hit["_source"]
        if last_reference is None:
            last_reference = decision["reference"]
        if decision["reference"] != last_reference:
            last_reference = decision["reference"]
            yield get_outcome()
            this_outcome = {}
            outcome_indices = set()
        outcome_indices.add(index)
        this_outcome = merge_in_decision(decision, this_outcome)
    if this_outcome:
        yield get_outcome()
