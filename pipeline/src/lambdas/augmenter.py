import os
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
        return doc

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


async def process_batch(refs):
    decisions = decisions_from_refs(client, refs=refs)
    return await map_docs(
        decisions,
        transform=augment_doc,
        dest_namespace="outcomes-augmented",
        dest_mapping={"dynamic": "strict", "properties": decision_augmented_mapping},
    )


def handler(event, context):
    augmenter_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(augmenter_event.refs))
