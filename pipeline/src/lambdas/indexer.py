import asyncio

from pipeline.transforms import transform_for_index

from . import get_docs


async def process_batch(refs):
    saved_refs = []
    async for update_doc, doc in get_docs(
        refs,
        destination_index_namespace="outcomes-indexed",
        destination_index_mapping="./index_mappings/outcomes_indexed.json",
    ):
        indexable = transform_for_index(doc)
        saved_ref = await update_doc(indexable)
        saved_refs.append(saved_ref)
    return saved_refs


def handler(event, context):
    return asyncio.run(process_batch(event))
