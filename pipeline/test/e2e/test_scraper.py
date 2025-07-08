from . import invoke_lambda, index_populated, index_for_test


async def test_scraper():
    async with index_for_test("outcomes-raw") as (index_name, index_suffix):
        assert not await index_populated(index_name)
        await invoke_lambda("scraper", {"limitItems": 1, "indexSuffix": index_suffix})
        assert await index_populated(index_name)
