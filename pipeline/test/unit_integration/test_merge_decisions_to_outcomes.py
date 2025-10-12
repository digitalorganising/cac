import pytest
from pipeline.decisions_to_outcomes import (
    merge_decisions_to_outcomes,
    merge_in_decision,
)


class MockOpenSearchClient:
    def __init__(self, search_results):
        self.search_results = search_results
        self.search_called = False
        self.search_args = None

    async def search(self, index, body):
        self.search_called = True
        self.search_args = {"index": index, "body": body}

        # Apply sorting if specified in the search body
        results = self.search_results.copy()
        if "sort" in body:
            results = self._apply_sort(results, body["sort"])

        return {
            "hits": {
                "hits": [
                    {
                        "_source": result,
                        "_index": "test-index",
                        "_id": result["reference"],
                    }
                    for result in results
                ]
            }
        }

    def _apply_sort(self, results, sort_specs):
        """Apply sorting to results based on sort specifications"""

        def get_sort_key(item):
            sort_values = []
            for sort_spec in sort_specs:
                for field, config in sort_spec.items():
                    order = config.get("order", "asc")
                    missing = config.get("missing", "_last")

                    # Get the value for this field
                    value = item.get(field)

                    # Handle missing values
                    if value is None:
                        if missing == "_last":
                            value = float("inf") if order == "asc" else float("-inf")
                        elif missing == "_first":
                            value = float("-inf") if order == "asc" else float("inf")
                        else:
                            value = missing

                    # Convert all values to strings for consistent comparison
                    if isinstance(value, str):
                        value = value.lower()
                    else:
                        value = str(value)

                    sort_values.append(value)

            return tuple(sort_values)

        # Sort the results
        sorted_results = sorted(results, key=get_sort_key)

        # Handle descending order by reversing the results for desc fields
        # This is a simplified approach - in a real implementation you'd need more sophisticated handling
        for sort_spec in sort_specs:
            for field, config in sort_spec.items():
                if config.get("order") == "desc":
                    # For simplicity, we'll just reverse the entire result
                    # In a real implementation, you'd need to handle mixed asc/desc sorts
                    sorted_results.reverse()
                    break

        return sorted_results


@pytest.fixture
def mock_client():
    """Create a mock OpenSearch client for testing"""
    return MockOpenSearchClient([])


@pytest.fixture
def sample_decisions():
    """Sample decision documents for testing"""
    return [
        {
            "reference": "TUR1/1234/2024",
            "document_type": "application_received",
            "document_content": "Application received on 2024-01-15",
            "document_url": "https://example.com/application_received",
            "extracted_data": {"decision_date": "2024-01-15"},
            "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
            "outcome_title": "Test Outcome 1",
            "last_updated": "2024-02-01T10:00:00Z",
        },
        {
            "reference": "TUR1/1234/2024",
            "document_type": "recognition_decision",
            "document_content": "Recognition granted on 2024-02-01",
            "document_url": "https://example.com/recognition_decision",
            "extracted_data": {"decision_date": "2024-02-01"},
            "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
            "outcome_title": "Test Outcome 1",
            "last_updated": "2024-02-01T10:00:00Z",
        },
        {
            "reference": "TUR1/5678/2024",
            "document_type": "application_received",
            "document_content": "Application received on 2024-01-20",
            "document_url": "https://example.com/application_received_2",
            "extracted_data": {"decision_date": "2024-01-20"},
            "outcome_url": "https://example.com/outcome/TUR1/5678/2024",
            "outcome_title": "Test Outcome 2",
            "last_updated": "2024-02-01T10:00:00Z",
        },
    ]


@pytest.fixture
def mock_client_with_data(sample_decisions):
    """Create a mock client with sample decision data"""
    return MockOpenSearchClient(sample_decisions)


def test_merge_in_decision_basic():
    """Test basic merging of a decision into an outcome"""
    decision = {
        "reference": "TUR1/1234/2024",
        "document_type": "application_received",
        "document_content": "Application received",
        "document_url": "https://example.com/application_received",
        "extracted_data": {"decision_date": "2024-01-15"},
    }
    outcome = {}

    result = merge_in_decision(decision, outcome)

    assert result["id"] == "TUR1/1234/2024"
    assert result["documents"]["application_received"] == "Application received"
    assert (
        result["document_urls"]["application_received"]
        == "https://example.com/application_received"
    )
    assert (
        result["extracted_data"]["application_received"]["decision_date"]
        == "2024-01-15"
    )


def test_merge_in_decision_with_existing_data():
    """Test merging when outcome already has some data"""
    decision = {
        "reference": "TUR1/1234/2024",
        "document_type": "recognition_decision",
        "document_content": "Recognition granted",
        "document_url": "https://example.com/recognition_decision",
        "extracted_data": {"decision_date": "2024-02-01"},
    }
    outcome = {
        "id": "TUR1/1234/2024",
        "documents": {"application_received": "Application received"},
        "document_urls": {
            "application_received": "https://example.com/application_received"
        },
        "extracted_data": {"application_received": {"decision_date": "2024-01-15"}},
    }

    result = merge_in_decision(decision, outcome)

    assert result["documents"]["application_received"] == "Application received"
    assert result["documents"]["recognition_decision"] == "Recognition granted"
    assert (
        result["document_urls"]["application_received"]
        == "https://example.com/application_received"
    )
    assert (
        result["document_urls"]["recognition_decision"]
        == "https://example.com/recognition_decision"
    )
    assert (
        result["extracted_data"]["application_received"]["decision_date"]
        == "2024-01-15"
    )
    assert (
        result["extracted_data"]["recognition_decision"]["decision_date"]
        == "2024-02-01"
    )


async def test_merge_decisions_to_outcomes_basic(mock_client_with_data):
    """Test basic merging of decisions to outcomes"""
    references = ["TUR1/1234/2024", "TUR1/5678/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client_with_data,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 2 outcomes: one for each reference
    assert len(outcomes) == 2
    assert outcomes[0][0].id == "TUR1/1234/2024"  # First reference
    assert outcomes[1][0].id == "TUR1/5678/2024"  # Second reference
    assert outcomes[0][1] == "test-index"  # Index should be passed through
    assert outcomes[1][1] == "test-index"

    # Check that search was called with correct parameters
    assert mock_client_with_data.search_called
    assert mock_client_with_data.search_args["index"] == "test-index"
    assert (
        mock_client_with_data.search_args["body"]["size"] == 2 * 15
    )  # len(references) * len(DocumentType)


async def test_merge_decisions_to_outcomes_single_reference(mock_client_with_data):
    """Test merging when there's only one reference"""
    references = ["TUR1/1234/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client_with_data,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 2 outcomes: one for each reference in the sample data
    assert len(outcomes) == 2
    outcome, index = outcomes[0]  # First reference outcome
    assert outcome.id == "TUR1/1234/2024"
    # Both decisions should be present in documents now that the bug is fixed
    assert "application_received" in outcome.documents
    assert "recognition_decision" in outcome.documents
    assert "application_received" in outcome.document_urls
    assert "recognition_decision" in outcome.document_urls
    assert "application_received" in outcome.extracted_data
    assert "recognition_decision" in outcome.extracted_data
    assert index == "test-index"


async def test_merge_decisions_to_outcomes_empty_results():
    """Test behavior when no decisions are found"""
    mock_client = MockOpenSearchClient([])

    references = ["TUR1/9999/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield no outcomes when no data found
    assert len(outcomes) == 0


async def test_merge_decisions_to_outcomes_multiple_decisions_per_reference():
    """Test merging multiple decisions for the same reference"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/1234/2024",
                "document_type": "application_received",
                "document_content": "Application received",
                "document_url": "https://example.com/application_received",
                "extracted_data": {"decision_date": "2024-01-15"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-01T10:00:00Z",
            },
            {
                "reference": "TUR1/1234/2024",
                "document_type": "recognition_decision",
                "document_content": "Recognition granted",
                "document_url": "https://example.com/recognition_decision",
                "extracted_data": {"decision_date": "2024-02-01"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-01T10:00:00Z",
            },
            {
                "reference": "TUR1/1234/2024",
                "document_type": "bargaining_decision",
                "document_content": "Bargaining unit defined",
                "document_url": "https://example.com/bargaining_decision",
                "extracted_data": {"decision_date": "2024-03-01"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-01T10:00:00Z",
            },
        ]
    )

    references = ["TUR1/1234/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with all 3 decisions merged in both documents and extracted_data
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    assert outcome.id == "TUR1/1234/2024"
    # All decisions should be in documents now that the bug is fixed
    assert len(outcome.documents) == 3
    assert "application_received" in outcome.documents
    assert "recognition_decision" in outcome.documents
    assert "bargaining_decision" in outcome.documents
    assert len(outcome.document_urls) == 3
    assert "application_received" in outcome.document_urls
    assert "recognition_decision" in outcome.document_urls
    assert "bargaining_decision" in outcome.document_urls
    assert len(outcome.extracted_data) == 3
    assert "application_received" in outcome.extracted_data
    assert "recognition_decision" in outcome.extracted_data
    assert "bargaining_decision" in outcome.extracted_data
    assert index == "test-index"


async def test_merge_decisions_to_outcomes_sort_order():
    """Test that decisions are processed in correct sort order"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/1234/2024",
                "document_type": "recognition_decision",
                "document_content": "Recognition granted",
                "document_url": "https://example.com/recognition_decision",
                "extracted_data": {"decision_date": "2024-02-01"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-01T10:00:00Z",
            },
            {
                "reference": "TUR1/1234/2024",
                "document_type": "application_received",
                "document_content": "Application received",
                "document_url": "https://example.com/application_received",
                "extracted_data": {"decision_date": "2024-01-15"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-01T10:00:00Z",
            },
        ]
    )

    references = ["TUR1/1234/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with both decisions merged in both documents and extracted_data
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    # Both decisions should be present in documents now that the bug is fixed
    assert "application_received" in outcome.documents
    assert "recognition_decision" in outcome.documents
    assert "application_received" in outcome.document_urls
    assert "recognition_decision" in outcome.document_urls
    # Both decisions should be in extracted_data
    assert "application_received" in outcome.extracted_data
    assert "recognition_decision" in outcome.extracted_data
    assert index == "test-index"


async def test_merge_decisions_to_outcomes_search_parameters(mock_client_with_data):
    """Test that search is called with correct parameters"""
    references = ["TUR1/1234/2024", "TUR1/5678/2024"]

    async for _ in merge_decisions_to_outcomes(
        mock_client_with_data,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        pass

    # Verify search parameters
    search_args = mock_client_with_data.search_args
    assert search_args["index"] == "test-index"
    assert search_args["body"]["size"] == 2 * 15  # len(references) * len(DocumentType)
    assert search_args["body"]["query"]["terms"]["reference"] == references


async def test_merge_decisions_to_outcomes_two_application_withdrawn():
    """Test merging two application_withdrawn documents - one with decision date, one without extracted data"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/1234/2024",
                "document_type": "application_withdrawn",
                "document_content": "Application withdrawn on 2024-02-15",
                "document_url": "https://example.com/application_withdrawn_1",
                "extracted_data": {"decision_date": "2024-02-15"},
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-15T10:00:00Z",
            },
            {
                "reference": "TUR1/1234/2024",
                "document_type": "application_withdrawn",
                "document_content": "Application withdrawn on 2024-03-01",
                "document_url": "https://example.com/application_withdrawn_2",
                "extracted_data": None,  # No extracted data for this one
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": None,
            },
        ]
    )

    references = ["TUR1/1234/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with both application_withdrawn documents merged
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    assert outcome.id == "TUR1/1234/2024"

    # Only one application_withdrawn document should be in documents (the last one overwrites)
    assert len(outcome.documents) == 1
    assert "application_withdrawn" in outcome.documents

    # Only one should be in document_urls (the last one overwrites)
    assert len(outcome.document_urls) == 1
    assert "application_withdrawn" in outcome.document_urls

    # Only one should be in extracted_data (the last one overwrites)
    assert len(outcome.extracted_data) == 1
    assert "application_withdrawn" in outcome.extracted_data

    # The extracted_data should contain the last one processed (the one with the actual extracted_data)
    application_withdrawn_data = outcome.extracted_data["application_withdrawn"]
    assert application_withdrawn_data is not None

    assert index == "test-index"


async def test_merge_decisions_to_outcomes_para_35_decision():
    """Test merging Paragraph 35 decision into outcome"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/1234/2024",
                "document_type": "para_35_decision",
                "document_content": "Paragraph 35 decision - application can proceed",
                "document_url": "https://example.com/para35_decision",
                "extracted_data": {
                    "decision_date": "2024-02-15",
                    "application_date": "2023-12-01",
                    "application_can_proceed": True,
                },
                "outcome_url": "https://example.com/outcome/TUR1/1234/2024",
                "outcome_title": "Test Outcome 1",
                "last_updated": "2024-02-15T10:00:00Z",
            }
        ]
    )

    references = ["TUR1/1234/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with para_35_decision merged
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    assert outcome.id == "TUR1/1234/2024"
    assert "para_35_decision" in outcome.documents
    assert (
        outcome.documents["para_35_decision"]
        == "Paragraph 35 decision - application can proceed"
    )
    assert "para_35_decision" in outcome.document_urls
    assert (
        outcome.document_urls["para_35_decision"]
        == "https://example.com/para35_decision"
    )
    assert "para_35_decision" in outcome.extracted_data
    assert outcome.extracted_data["para_35_decision"].decision_date == "2024-02-15"
    assert outcome.extracted_data["para_35_decision"].application_date == "2023-12-01"
    assert outcome.extracted_data["para_35_decision"].application_can_proceed is True
    assert index == "test-index"


async def test_merge_decisions_to_outcomes_para_35_decision_invalid():
    """Test merging Paragraph 35 decision with application_can_proceed=False"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/5678/2024",
                "document_type": "para_35_decision",
                "document_content": "Paragraph 35 decision - application cannot proceed",
                "document_url": "https://example.com/para35_decision_invalid",
                "extracted_data": {
                    "decision_date": "2024-02-15",
                    "application_date": "2023-12-01",
                    "application_can_proceed": False,
                },
                "outcome_url": "https://example.com/outcome/TUR1/5678/2024",
                "outcome_title": "Test Outcome 2",
                "last_updated": "2024-02-15T10:00:00Z",
            }
        ]
    )

    references = ["TUR1/5678/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with para_35_decision merged
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    assert outcome.id == "TUR1/5678/2024"
    assert "para_35_decision" in outcome.documents
    assert (
        outcome.documents["para_35_decision"]
        == "Paragraph 35 decision - application cannot proceed"
    )
    assert "para_35_decision" in outcome.document_urls
    assert (
        outcome.document_urls["para_35_decision"]
        == "https://example.com/para35_decision_invalid"
    )
    assert "para_35_decision" in outcome.extracted_data
    assert outcome.extracted_data["para_35_decision"].decision_date == "2024-02-15"
    assert outcome.extracted_data["para_35_decision"].application_date == "2023-12-01"
    assert outcome.extracted_data["para_35_decision"].application_can_proceed is False
    assert index == "test-index"


async def test_merge_decisions_to_outcomes_para_35_with_other_decisions():
    """Test merging Paragraph 35 decision along with other decisions for the same reference"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/9999/2024",
                "document_type": "para_35_decision",
                "document_content": "Paragraph 35 decision - application can proceed",
                "document_url": "https://example.com/para35_decision",
                "extracted_data": {
                    "decision_date": "2024-02-15",
                    "application_date": "2023-12-01",
                    "application_can_proceed": True,
                },
                "outcome_url": "https://example.com/outcome/TUR1/9999/2024",
                "outcome_title": "Test Outcome 3",
                "last_updated": "2024-03-15T10:00:00Z",
            },
            {
                "reference": "TUR1/9999/2024",
                "document_type": "acceptance_decision",
                "document_content": "Application accepted",
                "document_url": "https://example.com/acceptance_decision",
                "extracted_data": {
                    "decision_date": "2024-03-15",
                    "success": True,
                    "rejection_reasons": [],
                    "application_date": "2023-12-01",
                    "end_of_acceptance_period": "2024-03-10",
                    "bargaining_unit": {
                        "description": "All workers at Test Ltd",
                        "size_considered": True,
                        "size": 100,
                        "claimed_membership": 60,
                        "membership": 55,
                    },
                    "bargaining_unit_agreed": True,
                    "petition_signatures": 65,
                },
                "outcome_url": "https://example.com/outcome/TUR1/9999/2024",
                "outcome_title": "Test Outcome 3",
                "last_updated": "2024-03-15T10:00:00Z",
            },
        ]
    )

    references = ["TUR1/9999/2024"]

    outcomes = []
    async for outcome, index in merge_decisions_to_outcomes(
        mock_client,
        indices={"test-index"},
        non_pipeline_indices=set(),
        references=references,
    ):
        outcomes.append((outcome, index))

    # Should yield 1 outcome with both decisions merged
    assert len(outcomes) == 1
    outcome, index = outcomes[0]

    assert outcome.id == "TUR1/9999/2024"

    # Both decisions should be in documents
    assert len(outcome.documents) == 2
    assert "para_35_decision" in outcome.documents
    assert "acceptance_decision" in outcome.documents

    # Both decisions should be in document_urls
    assert len(outcome.document_urls) == 2
    assert "para_35_decision" in outcome.document_urls
    assert "acceptance_decision" in outcome.document_urls

    # Both decisions should be in extracted_data
    assert len(outcome.extracted_data) == 2
    assert "para_35_decision" in outcome.extracted_data
    assert "acceptance_decision" in outcome.extracted_data

    # Verify para_35_decision data
    assert outcome.extracted_data["para_35_decision"].application_can_proceed is True

    # Verify acceptance_decision data
    assert outcome.extracted_data["acceptance_decision"].success is True

    assert index == "test-index"
