import random
import string
import httpx
from contextlib import asynccontextmanager
from opensearchpy import AsyncOpenSearch

lambda_ports = {
    "scraper": 9000,
    "augmenter": 9001,
    "indexer": 9002,
}


def random_string(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def get_lambda_url(lambda_name):
    return f"http://localhost:{lambda_ports[lambda_name]}/2015-03-31/functions/function/invocations"


async def invoke_lambda(lambda_name, event):
    url = get_lambda_url(lambda_name)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=event)
        print(response.text)
        return response.json()


opensearch_client = AsyncOpenSearch(
    hosts=["http://localhost:9200"],
    verify_certs=False,
    ssl_show_warn=False,
)


async def index_populated(index_name) -> bool:
    exists = await opensearch_client.indices.exists(index=index_name)
    if not exists:
        return False
    count_response = await opensearch_client.count(index=index_name)
    return count_response["count"] > 0


@asynccontextmanager
async def with_index(namespace: str):
    """
    Context manager that provides an index namespace with a random suffix.

    Args:
        namespace: The base namespace for the index

    Yields:
        str: The full index name with random suffix

    Example:
        async with index_namespace("outcomes-raw") as index_name:
            # Use index_name for testing
            pass
        # Index is automatically deleted after the context exits
    """
    index_suffix = random_string()
    index_name = f"{namespace}-{index_suffix}"

    try:
        yield index_name, index_suffix
    finally:
        # Clean up: delete the index if it exists
        try:
            exists = await opensearch_client.indices.exists(index=index_name)
            if exists:
                await opensearch_client.indices.delete(index=index_name)
        except Exception as e:
            # Log but don't raise - cleanup failures shouldn't break tests
            print(f"Warning: Failed to delete index {index_name}: {e}")
