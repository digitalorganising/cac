import asyncio
import os
from pydantic import BaseModel, Field
from opensearchpy import helpers

from pipeline.services.opensearch_utils import (
    create_client,
    get_auth,
    ensure_index_mapping,
)


client = create_client(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    auth=get_auth(credentials_secret=os.getenv("OPENSEARCH_CREDENTIALS_SECRET")),
    async_client=True,
)


# https://stackoverflow.com/a/74988928
def lambda_friendly_run_async(awaitable):
    loop = asyncio.get_event_loop()
    if loop.is_closed():  # I don't know why
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(awaitable)


def get_index_suffix(index_name):
    if not index_name.startswith("outcomes"):
        return None

    # Split by '-' and get the last part
    parts = index_name.split("-")
    return parts[-1] if len(parts) > 1 else None


class DocumentRef(BaseModel):
    id: str = Field(alias="_id")
    index: str = Field(alias="_index")


class RefsEvent(BaseModel):
    refs: list[DocumentRef]


def destination_index(*, source_index, dest_namespace):
    index_suffix = get_index_suffix(source_index)
    dest_index = f"{dest_namespace}-{index_suffix}" if index_suffix else dest_namespace
    return dest_index


async def map_docs(docs_source, *, transform, dest_namespace, dest_mapping):
    seen_indices = set()

    async def update_actions():
        async for doc, ref in docs_source:
            transformed_doc = await transform(doc)
            dest_index = destination_index(
                source_index=ref.index, dest_namespace=dest_namespace
            )
            if dest_index not in seen_indices:
                await ensure_index_mapping(client, dest_index, dest_mapping)
                seen_indices.add(dest_index)
            yield {
                "_op_type": "update",
                "_index": dest_index,
                "_id": ref.id,
                "doc": transformed_doc,
                "doc_as_upsert": True,
                "retry_on_conflict": 3,
            }

    results = []
    async for ok, result in helpers.async_streaming_bulk(
        client, update_actions(), index=dest_namespace
    ):
        if not ok:
            raise Exception("Failed to index item", result)
        update = result["update"]
        ref = DocumentRef(
            _id=update["_id"],
            _index=update["_index"],
        )
        results.append(ref.model_dump(by_alias=True))
    return results
