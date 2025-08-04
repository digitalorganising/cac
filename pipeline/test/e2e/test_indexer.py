from . import invoke_lambda, index_populated, indexer, load_docs

test_withdrawal_docs = [
    {
        "id": "TUR1/1234(2025):application_withdrawn",
        "reference": "TUR1/1234(2025)",
        "document_type": "application_withdrawn",
        "outcome_title": "Test union & test employer",
        "document_content": "test",
        "document_url": "http://test.outcome/1234/withdrawn",
        "extracted_data": {
            "decision_date": "02 January 2025",
        },
    },
    {
        "id": "TUR1/1234(2025):application_received",
        "reference": "TUR1/1234(2025)",
        "document_type": "application_received",
        "outcome_title": "Test union & test employer",
        "document_content": "test",
        "document_url": "http://test.outcome/1234/received",
        "extracted_data": {
            "decision_date": "01 January 2025",
        },
    },
]

test_decision_docs = [
    {
        "id": "TUR1/1234(2025):application_withdrawn",
        "reference": "TUR1/1234(2025)",
        "last_updated": "2025-01-01",
        "outcome_url": "http://test.outcome/1234",
        "outcome_title": "Test union & test employer",
        "document_type": "application_withdrawn",
        "document_content": "test",
        "document_url": "http://test.outcome/1234/withdrawn",
        "extracted_data": None,
    },
    {
        "id": "TUR1/1057(2018):whether_to_ballot_decision",
        "reference": "TUR1/1057(2018)",
        "outcome_title": "UNISON & Abbey Healthcare",
        "outcome_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare",
        "document_type": "whether_to_ballot_decision",
        "document_content": "test",
        "document_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/whether-to-ballot-decision",
        "extracted_data": {
            "decision_date": "23 July 2018",
            "decision_to_ballot": True,
            "majority_membership": False,
            "qualifying_conditions": [],
        },
    },
    {
        "id": "TUR1/1057(2018):acceptance_decision",
        "reference": "TUR1/1057(2018)",
        "outcome_title": "UNISON & Abbey Healthcare",
        "outcome_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare",
        "document_type": "acceptance_decision",
        "document_content": "test",
        "document_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/acceptance-decision",
        "extracted_data": {
            "decision_date": "17 July 2018",
            "bargaining_unit": {
                "claimed_membership": 46,
                "size": 115,
                "description": "All Abbey Healthcare employees, including home manager, working in the residential care home of Farnworth Care Home",
                "size_considered": True,
                "membership": 42,
            },
            "success": True,
            "rejection_reasons": [],
            "application_date": "21 June 2018",
            "end_of_acceptance_period": "20 July 2018",
            "bargaining_unit_agreed": False,
            "petition_signatures": 81,
        },
    },
    {
        "id": "TUR1/1057(2018):recognition_decision",
        "reference": "TUR1/1057(2018)",
        "last_updated": "2018-09-20",
        "outcome_title": "UNISON & Abbey Healthcare",
        "outcome_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare",
        "document_type": "recognition_decision",
        "document_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/recognition-decision",
        "document_content": "test",
        "extracted_data": {
            "decision_date": "20 September 2018",
            "union_recognized": False,
            "ballot": {
                "votes_against": 4,
                "eligible_workers": 115,
                "end_ballot_period": "14 September 2018",
                "spoiled_ballots": 0,
                "start_ballot_period": "28 August 2018",
                "votes_in_favor": 28,
            },
            "form_of_ballot": "Postal",
            "good_relations_contested": False,
        },
    },
]


async def test_indexer(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test(
        "outcomes-augmented", initial_docs=test_decision_docs
    ) as augmented, index_for_test(
        "application-withdrawals", initial_docs=test_withdrawal_docs, no_suffix=True
    ) as withdrawals, index_for_test(
        "outcomes-indexed", suffix=augmented.suffix
    ) as indexed:
        refs = [
            {"_id": d["id"], "_index": augmented.index_name}
            for d in test_decision_docs[:3]
        ]
        await invoke_lambda("indexer", {"refs": refs})
        assert await index_populated(opensearch_client, indexed.index_name)

        results = await opensearch_client.search(index=indexed.index_name)
        hits = results["hits"]["hits"]

        assert len(hits) == 2
        merged_outcome = next(h for h in hits if h["_id"] == "TUR1/1057(2018)")
        withdrawn_outcome = next(h for h in hits if h["_id"] == "TUR1/1234(2025)")

        assert "display" in merged_outcome["_source"]
        assert "display" in withdrawn_outcome["_source"]
