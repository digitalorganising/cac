from . import invoke_lambda, indexer


async def test_scraper(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test("outcomes-raw") as raw:
        result = await invoke_lambda(
            "scraper", {"limitItems": 1, "indexSuffix": raw.suffix}
        )
        assert len(result) >= 1

        # Checking whether we pass on IDs of duplicates
        result_2 = await invoke_lambda(
            "scraper", {"limitItems": 1, "indexSuffix": raw.suffix}
        )
        assert set(r["_id"] for r in result).isdisjoint(r["_id"] for r in result_2)
