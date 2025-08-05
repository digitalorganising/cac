from pipeline.transforms.augmentation import augment_doc
from pipeline.types.decisions import DecisionRaw, decision_augmented_mapping

from . import map_docs, RefsEvent, lambda_friendly_run_async, DocumentRef, client


async def decisions_from_refs(client, *, refs):
    res = await client.mget(
        body={"docs": [ref.model_dump(by_alias=True) for ref in refs]}
    )
    for doc in res["docs"]:
        ref = DocumentRef(
            _id=doc["_id"],
            _index=doc["_index"],
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
