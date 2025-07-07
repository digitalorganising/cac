import asyncio

from pipeline.transforms.augmentation import augment_doc

from . import get_docs


async def process_batch(refs):
    saved_refs = []
    async for update_doc, doc in get_docs(
        refs,
        destination_index_namespace="outcomes-augmented",
        destination_index_mapping="./index_mappings/outcomes_augmented.json",
    ):
        augmented_doc = await augment_doc(doc)
        saved_ref = await update_doc(augmented_doc)
        saved_refs.append(saved_ref)
    return saved_refs


# Event is an array of { "_id": str, "_index": str }
def handler(event, context):
    return asyncio.run(process_batch(event))
