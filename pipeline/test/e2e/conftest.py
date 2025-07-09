import pytest
from opensearchpy import AsyncOpenSearch


@pytest.fixture
async def opensearch_client():
    client = AsyncOpenSearch(
        hosts=["http://localhost:9200"],
        verify_certs=False,
        ssl_show_warn=False,
    )
    yield client
    await client.close()
