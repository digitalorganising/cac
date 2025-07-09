from . import invoke_lambda, index_populated, indexer


async def test_scraper(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test("outcomes-raw") as (
        index_name,
        index_suffix,
    ):
        assert not await index_populated(opensearch_client, index_name)
        await invoke_lambda("scraper", {"limitItems": 1, "indexSuffix": index_suffix})
        assert await index_populated(opensearch_client, index_name)
