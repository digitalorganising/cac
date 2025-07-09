from . import invoke_lambda, index_populated, indexer, load_docs


test_doc = {
    "reference": "TUR1/1057(2018)",
    "last_updated": "2018-09-20T11:55:08+01:00",
    "outcome_url": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare",
    "outcome_title": "UNISON & Abbey Healthcare",
    "documents": {
        "whether_to_ballot_decision": "test",
        "acceptance_decision": "test",
        "recognition_decision": "test",
    },
    "document_urls": {
        "whether_to_ballot_decision": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/whether-to-ballot-decision",
        "acceptance_decision": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/acceptance-decision",
        "recognition_decision": "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/recognition-decision",
    },
    "extracted_data": {
        "whether_to_ballot_decision": {
            "decision_date": "23 July 2018",
            "decision_to_ballot": True,
            "majority_membership": False,
            "qualifying_conditions": [],
        },
        "acceptance_decision": {
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
        "recognition_decision": {
            "decision_date": "20 September 2018",
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
            "union_recognized": False,
        },
    },
}


async def test_indexer(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test(
        "outcomes-augmented", initial_docs=[test_doc]
    ) as augmented, index_for_test(
        "outcomes-indexed", suffix=augmented.suffix
    ) as indexed:
        refs = [{"_id": test_doc["reference"], "_index": augmented.index_name}]
        await invoke_lambda("indexer", {"refs": refs})
        assert await index_populated(opensearch_client, indexed.index_name)
