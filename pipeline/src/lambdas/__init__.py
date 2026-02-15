import asyncio
import concurrent.futures
import os
from typing import Generic, TypeVar

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


def run_in_loop(loop, coro):
    """Runs an async function in an already-running loop, synchronously."""
    future = concurrent.futures.Future()

    # Schedule coroutine execution in the event loop
    async def runner():
        try:
            result = await coro
        except Exception as e:
            loop.call_soon_threadsafe(future.set_exception, e)
        else:
            loop.call_soon_threadsafe(future.set_result, result)

    # Schedule the runner inside the loop
    loop.call_soon_threadsafe(asyncio.create_task, runner())

    # Block synchronously until the result is ready
    return future.result()


# https://stackoverflow.com/a/74988928
def lambda_friendly_run_async(awaitable):
    loop = asyncio.get_event_loop()
    if loop.is_closed():  # I don't know why
        loop = asyncio.new_event_loop()
    if loop.is_running():
        return run_in_loop(loop, awaitable)
    else:
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
    passthrough: bool = False


RefsEventRefT = TypeVar("RefsEventRefT", bound=DocumentRef, default=DocumentRef)


class RefsEvent(BaseModel, Generic[RefsEventRefT]):
    refs: list[RefsEventRefT]


def destination_index(*, source_index, dest_namespace):
    index_suffix = get_index_suffix(source_index)
    dest_index = f"{dest_namespace}-{index_suffix}" if index_suffix else dest_namespace
    return dest_index


async def map_docs(
    docs_source,
    *,
    transform,
    dest_namespace,
    dest_mapping,
    refresh_on_complete=True,
    result_transform=None,
):
    seen_indices = set()
    result_map = {}

    async def update_actions():
        async for doc, ref in docs_source:
            dest_index = destination_index(
                source_index=ref.index, dest_namespace=dest_namespace
            )
            if dest_index not in seen_indices:
                await ensure_index_mapping(client, dest_index, dest_mapping)
                seen_indices.add(dest_index)

            common_action = {
                "_op_type": "update",
                "_index": dest_index,
                "_id": ref.id,
                "retry_on_conflict": 3,
            }

            if ref.passthrough:
                result_map[ref.id] = (
                    result_transform(doc.model_dump(by_alias=True))
                    if result_transform
                    else {}
                )
                yield {
                    **common_action,
                    "doc": {},
                }
            else:
                transformed_doc = await transform(doc)
                if not transformed_doc:
                    continue
                result_map[ref.id] = (
                    result_transform(transformed_doc) if result_transform else {}
                )
                yield {
                    **common_action,
                    "doc": transformed_doc,
                    "doc_as_upsert": True,
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
        additional_fields = result_map.pop(update["_id"], {})
        results.append({**ref.model_dump(by_alias=True), **additional_fields})

    if refresh_on_complete:
        indices = {r["_index"] for r in results}
        for index in indices:
            await client.indices.refresh(index=index)

    return results
