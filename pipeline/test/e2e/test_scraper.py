from . import invoke_lambda, index_populated, indexer


async def test_scraper(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test("outcomes-raw") as raw:
        assert not await index_populated(opensearch_client, raw.index_name)
        result = await invoke_lambda(
            "scraper", {"limitItems": 1, "indexSuffix": raw.suffix}
        )
        assert len(result) >= 1
        assert await index_populated(opensearch_client, raw.index_name)
