from . import invoke_lambda, index_populated, indexer

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
]


async def test_augmenter(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test(
        "outcomes-raw", initial_docs=test_docs
    ) as raw, index_for_test("outcomes-augmented", suffix=raw.suffix) as augmented:
        refs = [{"_id": t["id"], "_index": raw.index_name} for t in test_docs]
        await invoke_lambda("augmenter", {"refs": refs})
        assert await index_populated(opensearch_client, augmented.index_name)

        results = await opensearch_client.search(index=augmented.index_name)
        hits = results["hits"]["hits"]
        acceptance_outcome = next(h for h in hits if h["_id"] == "test1")["_source"]
        withdrawn_outcome = next(h for h in hits if h["_id"] == "test2")["_source"]

        assert len(acceptance_outcome["extracted_data"]) > 0
        assert withdrawn_outcome["extracted_data"] is None
