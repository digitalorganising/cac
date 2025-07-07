import os

from pipeline.services.opensearch_utils import (
    create_client,
    get_auth,
    ensure_index_mapping,
)


client = create_client(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    auth=get_auth(),
    async_client=True,
)


def get_index_suffix(index_name):
    if not index_name.startswith("outcomes"):
        return None

    # Split by '-' and get the last part
    parts = index_name.split("-")
    return parts[-1] if len(parts) > 1 else None


async def get_docs(refs, *, destination_index_namespace, destination_index_mapping):
    response = await client.mget(body={"docs": refs})
    seen_indices = set()
    for hit in response["docs"]:
        if hit["found"]:
            index = hit["_index"]
            original_doc = hit["_source"]
            id = hit["_id"]
            index_suffix = get_index_suffix(index)

            dest_index = (
                f"{destination_index_namespace}-{index_suffix}"
                if index_suffix
                else destination_index_namespace
            )
            if dest_index not in seen_indices:
                await ensure_index_mapping(
                    client, dest_index, destination_index_mapping
                )
                seen_indices.add(dest_index)

            async def update_doc(updated_doc):
                res = await client.update(
                    index=dest_index,
                    id=id,
                    body={
                        "doc": updated_doc,
                        "doc_as_upsert": True,
                    },
                    retry_on_conflict=3,
                )
                return {
                    "_id": res["_id"],
                    "_index": res["_index"],
                }

            yield update_doc, original_doc
