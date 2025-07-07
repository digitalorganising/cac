import asyncio
import os

from pipeline.services.opensearch_utils import (
    create_client,
    get_auth,
    ensure_index_mapping,
)
from pipeline.transforms.augmentation import augment_doc

from . import get_index_suffix


client = create_client(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    auth=get_auth(),
    async_client=True,
)


async def get_docs(refs):
    response = await client.mget(body={"docs": refs})
    for hit in response["docs"]:
        if hit["found"]:
            yield hit["_index"], hit["_source"]


async def process_batch(refs):
    seen_indices = set()
    saved_refs = []
    async for index, doc in get_docs(refs):
        augmented_doc = await augment_doc(doc)
        if index not in seen_indices:
            await ensure_index_mapping(
                client, index, "./index_mappings/outcomes_augmented.json"
            )
            seen_indices.add(index)
        save_index_suffix = get_index_suffix(index)
        save_index = (
            f"outcomes-augmented-{save_index_suffix}"
            if save_index_suffix
            else "outcomes-augmented"
        )
        res = await client.update(
            index=save_index,
            id=doc["reference"],
            body={
                "doc": augmented_doc,
                "doc_as_upsert": True,
            },
            retry_on_conflict=3,
        )
        saved_refs.append(
            {
                "_id": res["_id"],
                "_index": res["_index"],
            }
        )
    return saved_refs


# Event is an array of { "_id": str, "_index": str }
def handler(event, context):
    return asyncio.run(process_batch(event))
