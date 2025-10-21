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


test_docs = [
    {
        "id": "test1",
        "reference": "TUR1/1234/2024",
        "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
        "outcome_title": "Test Outcome 1",
        "document_type": "acceptance_decision",
        "document_content": "test",
        "document_url": "https://example.com/document/test1",
        "last_updated": "2024-02-01T10:00:00Z",
    },
    {
        "id": "test2",
        "reference": "TUR1/5678/2024",
        "outcome_url": "https://example.com/outcome/TUR1/5678/2024",
        "outcome_title": "Test Outcome 2",
        "document_type": "application_withdrawn",
        "document_content": "test",
        "document_url": "https://example.com/document/test2",
        "last_updated": "2024-02-01T10:00:00Z",
    },
    {
        "id": "test3",
        "reference": "TUR1/9101/2024",
        "outcome_url": "https://example.com/outcome/TUR1/9101/2024",
        "outcome_title": "Test Outcome 3",
        "document_type": "acceptance_decision",
        "document_content": "test",
        "document_url": "https://example.com/document/test3",
        "last_updated": "2024-02-01T10:00:00Z",
    },
]


async def test_scraper_redrive(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test("outcomes-raw", initial_docs=test_docs) as raw:
        result = await invoke_lambda(
            "scraper",
            {
                "indexSuffix": raw.suffix,
                "redrive": {"complete": True, "augment": False},
            },
        )
        assert len(result) == len(test_docs)
        assert "test1" in [r["_id"] for r in result]
        assert "test2" in [r["_id"] for r in result]
        assert "test3" in [r["_id"] for r in result]
