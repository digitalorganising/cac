import os
from pipeline.transforms import get_parties
from pipeline.types.decisions import (
    DecisionRaw,
    DecisionAugmented,
    decision_augmented_mapping,
    DocumentType,
)

from . import map_docs, RefsEvent, lambda_friendly_run_async, DocumentRef, client

if os.getenv("MOCK_LLM"):
    from pipeline.transforms.mock_augmentation import get_extracted_data
else:
    from pipeline.transforms.augmentation import get_extracted_data


async def augment_doc(doc: DecisionRaw):
    if doc.document_type == DocumentType.derecognition_decision.value:
        return doc.model_dump(by_alias=True)

    extracted_data = await get_extracted_data(doc.document_type, doc.document_content)
    model = DecisionAugmented.from_raw(doc, extracted_data)
    return model.model_dump(by_alias=True)


async def decisions_from_refs(client, *, refs):
    passthroughs = {ref.id for ref in refs if ref.passthrough}
    res = await client.mget(
        body={
            "docs": [
                ref.model_dump(by_alias=True, exclude={"passthrough"}) for ref in refs
            ]
        }
    )
    for doc in res["docs"]:
        ref = DocumentRef(
            _id=doc["_id"],
            _index=doc["_index"],
            passthrough=doc["_id"] in passthroughs,
        )
        yield DecisionRaw.model_validate(doc["_source"]), ref


def transform_for_next_step(transformed_doc):
    if transformed_doc["document_type"] != DocumentType.acceptance_decision.value:
        return {}
    extracted_data = transformed_doc.get("extracted_data", None)
    if not extracted_data:
        return {}
    parties = get_parties(transformed_doc["outcome_title"])
    bargaining_unit = extracted_data["bargaining_unit"]
    return {
        "name": parties["employer"],
        "unions": parties["unions"],
        "application_date": extracted_data["decision_date"],
        "bargaining_unit": bargaining_unit["description"],
        "locations": bargaining_unit.get("locations", None),
    }


async def process_batch(refs):
    decisions = decisions_from_refs(client, refs=refs)
    return await map_docs(
        decisions,
        transform=augment_doc,
        dest_namespace="outcomes-augmented",
        dest_mapping={"dynamic": "strict", "properties": decision_augmented_mapping},
        result_transform=transform_for_next_step,
    )


def handler(event, context):
    augmenter_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(augmenter_event.refs))
