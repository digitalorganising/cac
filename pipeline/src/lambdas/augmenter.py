import os
from pipeline.transforms import get_parties
from pipeline.types.decisions import (
    DecisionRaw,
    DecisionAugmented,
    decision_augmented_mapping,
    DocumentType,
)

from . import (
    RefEvent,
    client,
    DocumentRef,
    lambda_friendly_run_async,
    map_doc,
)

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


async def process_ref(ref: DocumentRef):
    src = await client.get(index=ref.index, id=ref.id)
    decision = DecisionRaw.model_validate(src["_source"])
    return await map_doc(
        decision,
        ref,
        transform=augment_doc,
        dest_namespace="outcomes-augmented",
        dest_mapping={"dynamic": "strict", "properties": decision_augmented_mapping},
        result_transform=transform_for_next_step,
    )


def handler(event, context):
    augmenter_event = RefEvent.model_validate(event)
    return lambda_friendly_run_async(process_ref(augmenter_event.ref))
