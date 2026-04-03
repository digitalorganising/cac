import asyncio
import concurrent.futures
import os

from pydantic import BaseModel, ConfigDict, Field

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
    """OpenSearch document pointer; extra keys (e.g. disambiguated_company) allowed for indexer."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(alias="_id")
    index: str = Field(alias="_index")
    passthrough: bool = False


class RefEvent(BaseModel):
    ref: DocumentRef


def destination_index(*, source_index, dest_namespace):
    index_suffix = get_index_suffix(source_index)
    dest_index = f"{dest_namespace}-{index_suffix}" if index_suffix else dest_namespace
    return dest_index


async def map_doc(
    doc,
    ref: DocumentRef,
    *,
    transform,
    dest_namespace: str,
    dest_mapping,
    dest_id: str | None = None,
    refresh_on_complete: bool = True,
    result_transform=None,
):
    """Transform one source document and upsert it into the destination index."""
    dest_index = destination_index(
        source_index=ref.index, dest_namespace=dest_namespace
    )
    await ensure_index_mapping(client, dest_index, dest_mapping)

    doc_id = dest_id if dest_id is not None else ref.id

    if ref.passthrough:
        await client.update(
            index=dest_index,
            id=doc_id,
            body={"doc": {}},
            params={"retry_on_conflict": 3},
        )
        if refresh_on_complete:
            await client.indices.refresh(index=dest_index)
        augmented = await client.get(index=dest_index, id=doc_id)
        if not augmented.get("found"):
            raise ValueError(f"Document missing after passthrough update: {doc_id}")
        extra = result_transform(augmented["_source"]) if result_transform else {}
    else:
        if asyncio.iscoroutinefunction(transform):
            transformed = await transform(doc)
        else:
            transformed = transform(doc)
        if not transformed:
            return None
        await client.update(
            index=dest_index,
            id=doc_id,
            body={"doc": transformed, "doc_as_upsert": True},
            params={"retry_on_conflict": 3},
        )
        if refresh_on_complete:
            await client.indices.refresh(index=dest_index)
        extra = result_transform(transformed) if result_transform else {}

    return {
        **DocumentRef(
            _id=doc_id, _index=dest_index, passthrough=ref.passthrough
        ).model_dump(by_alias=True),
        **extra,
    }
