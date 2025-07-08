from . import invoke_lambda, index_populated, with_index


async def test_scraper():
    async with with_index("outcomes-raw") as (index_name, index_suffix):
        assert not await index_populated(index_name)
        await invoke_lambda("scraper", {"limitItems": 1, "indexSuffix": index_suffix})
        assert await index_populated(index_name)
