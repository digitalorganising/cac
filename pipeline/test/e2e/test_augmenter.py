from . import invoke_lambda, index_populated, indexer, load_docs

test_docs = [
    {
        "reference": "test1",
        "documents": {
            "acceptance_decision": "test",
        },
    },
    {
        "reference": "test2",
        "documents": {
            "application_withdrawn": None,
        },
    },
]

test_withdrawals = [
    {
        "reference": "test2",
        "application_withdrawn": "01/02/2024",
        "application_received": "01/01/2024",
    },
]


async def test_augmenter(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test("outcomes-raw") as (
        raw_index,
        index_suffix,
    ), index_for_test("outcomes-augmented", suffix=index_suffix) as (
        augmented_index,
        _,
    ), index_for_test(
        "application-withdrawals", no_suffix=True
    ) as (
        withdrawals_index,
        _,
    ):
        await load_docs(opensearch_client, raw_index, test_docs)
        await load_docs(opensearch_client, withdrawals_index, test_withdrawals)

        refs = [{"_id": t["reference"], "_index": raw_index} for t in test_docs]
        await invoke_lambda("augmenter", {"refs": refs})
        assert await index_populated(opensearch_client, augmented_index)

        results = await opensearch_client.search(index=augmented_index)
        hits = results["hits"]["hits"]
        acceptance_outcome = next(h for h in hits if h["_id"] == "test1")["_source"]
        withdrawn_outcome = next(h for h in hits if h["_id"] == "test2")["_source"]

        assert "acceptance_decision" in acceptance_outcome["extracted_data"]
        new_withdrawn = withdrawn_outcome["extracted_data"]["application_withdrawn"]
        new_received = withdrawn_outcome["extracted_data"]["application_received"]
        assert new_withdrawn["decision_date"] == "2024-02-01"
        assert new_received["decision_date"] == "2024-01-01"
