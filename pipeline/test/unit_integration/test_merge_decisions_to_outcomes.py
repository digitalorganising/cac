import copy

import pytest
from pydantic import ValidationError

from pipeline.decisions_to_outcomes import (
    merge_decisions,
    merge_decisions_to_outcome,
    merge_without_none,
)
from pipeline.types.documents import DocumentType


class MockOpenSearchClient:
    def __init__(self, search_results):
        self.search_results = search_results
        self.search_called = False
        self.search_args = None
        self.search_calls = []

    async def search(self, index, body):
        self.search_called = True
        self.search_args = {"index": index, "body": body}
        self.search_calls.append({"index": index, "body": body})

        results = list(self.search_results)
        query = body.get("query") or {}
        term = query.get("term") or {}
        if "reference" in term:
            ref_val = term["reference"]
            results = [r for r in results if r.get("reference") == ref_val]

        results = copy.deepcopy(results)
        if "sort" in body:
            results = self._apply_sort(results, body["sort"])

        return {
            "hits": {
                "hits": [
                    {
                        "_source": result,
                        "_index": "test-index",
                        "_id": result.get("reference", "unknown"),
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


def test_merge_decisions_basic():
    """Test basic merging of a decision into an outcome"""
    decision = {
        "reference": "TUR1/1234/2024",
        "document_type": "application_received",
        "document_content": "Application received",
        "document_url": "https://example.com/application_received",
        "extracted_data": {"decision_date": "2024-01-15"},
    }
    outcome = {}

    result = merge_decisions(outcome, decision)

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


def test_merge_decisions_with_existing_data():
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

    result = merge_decisions(outcome, decision)

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
    for ref in references:
        outcome = await merge_decisions_to_outcome(
            mock_client_with_data,
            index="test-index",
            non_pipeline_indices=set(),
            reference=ref,
        )
        assert outcome is not None
        outcomes.append(outcome)

    assert len(outcomes) == 2
    assert outcomes[0].id == "TUR1/1234/2024"
    assert outcomes[1].id == "TUR1/5678/2024"

    assert mock_client_with_data.search_called
    assert len(mock_client_with_data.search_calls) == 2
    assert mock_client_with_data.search_calls[0]["body"]["size"] == len(DocumentType)
    assert (
        mock_client_with_data.search_calls[0]["body"]["query"]["term"]["reference"]
        == "TUR1/1234/2024"
    )


async def test_merge_decisions_to_outcomes_single_reference(mock_client_with_data):
    """Test merging when there's only one reference (two decisions in the index)"""
    outcome = await merge_decisions_to_outcome(
        mock_client_with_data,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1234/2024",
    )
    assert outcome is not None
    assert outcome.id == "TUR1/1234/2024"
    assert "application_received" in outcome.documents
    assert "recognition_decision" in outcome.documents
    assert "application_received" in outcome.document_urls
    assert "recognition_decision" in outcome.document_urls
    assert "application_received" in outcome.extracted_data
    assert "recognition_decision" in outcome.extracted_data


async def test_merge_decisions_to_outcomes_empty_results():
    """Test behavior when no decisions are found"""
    mock_client = MockOpenSearchClient([])

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/9999/2024",
    )
    assert outcome is None


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

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1234/2024",
    )
    assert outcome is not None

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

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1234/2024",
    )
    assert outcome is not None

    assert "application_received" in outcome.documents
    assert "recognition_decision" in outcome.documents
    assert "application_received" in outcome.document_urls
    assert "recognition_decision" in outcome.document_urls
    assert "application_received" in outcome.extracted_data
    assert "recognition_decision" in outcome.extracted_data


async def test_merge_decisions_to_outcomes_search_parameters(mock_client_with_data):
    """Test that search is called with correct parameters"""
    references = ["TUR1/1234/2024", "TUR1/5678/2024"]

    for ref in references:
        await merge_decisions_to_outcome(
            mock_client_with_data,
            index="test-index",
            non_pipeline_indices=set(),
            reference=ref,
        )

    assert len(mock_client_with_data.search_calls) == 2
    queried = {
        c["body"]["query"]["term"]["reference"] for c in mock_client_with_data.search_calls
    }
    assert queried == set(references)
    for call in mock_client_with_data.search_calls:
        assert call["index"] == "test-index"
        assert call["body"]["size"] == len(DocumentType)


async def test_merge_decisions_to_outcomes_two_application_withdrawn():
    """Test merging two application_withdrawn documents - one with decision date, one without extracted data"""
    mock_client = MockOpenSearchClient(
        [
            {
                "reference": "TUR1/1081(2018)",
                "document_url": "https://www.whatdotheyknow.com/request/information_on_withdrawn_applica",
                "id": "TUR1/1081(2018):application_received",
                "document_type": "application_received",
                "document_content": "Application to TRS Cash & Carry Limited from GMB received on 2018-12-13T00:00:00+00:00.",
                "extracted_data": {"decision_date": "2018-12-13"},
            },
            {
                "reference": "TUR1/1081(2018)",
                "document_url": "https://www.whatdotheyknow.com/request/information_on_withdrawn_applica",
                "id": "TUR1/1081(2018):application_withdrawn",
                "last_updated": "2018-12-20T00:00:00+00:00",
                "document_type": "application_withdrawn",
                "document_content": "Application to TRS Cash & Carry Limited withdrawn by GMB on 2018-12-20T00:00:00+00:00.",
                "extracted_data": {"decision_date": "2018-12-20"},
            },
            {
                "id": "TUR1/1081(2018):application_withdrawn",
                "reference": "TUR1/1081(2018)",
                "outcome_url": "https://www.gov.uk/government/publications/cac-outcome-gmb-trs-cash-carry-limited2",
                "outcome_title": "GMB & TRS Cash & Carry Limited(2)",
                "document_type": "application_withdrawn",
                "last_updated": "2018-12-14T14:23:00+00:00",
                "document_content": None,
                "document_url": "https://www.gov.uk/government/publications/cac-outcome-gmb-trs-cash-carry-limited2/application-withdrawn",
                "extracted_data": None,
            },
        ]
    )

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1081(2018)",
    )
    assert outcome is not None

    assert outcome.id == "TUR1/1081(2018)"

    application_withdrawn_data = outcome.extracted_data["application_withdrawn"]
    assert application_withdrawn_data is not None
    assert application_withdrawn_data.decision_date == "2018-12-20"


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

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1234/2024",
    )
    assert outcome is not None

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

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/5678/2024",
    )
    assert outcome is not None

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

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/9999/2024",
    )
    assert outcome is not None

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


async def test_merge_decisions_to_outcomes_validation_error_last_updated():
    """Test that ValidationError with last_updated field does not yield anything"""
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
                # Missing last_updated field to trigger ValidationError
            }
        ]
    )

    outcome = await merge_decisions_to_outcome(
        mock_client,
        index="test-index",
        non_pipeline_indices=set(),
        reference="TUR1/1234/2024",
    )
    assert outcome is None


async def test_merge_decisions_to_outcomes_validation_error_other_field():
    """Test that ValidationError with other fields raises the exception"""
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
                "last_updated": "invalid-date-format",  # Invalid date format to trigger ValidationError
            }
        ]
    )

    with pytest.raises(ValidationError):
        await merge_decisions_to_outcome(
            mock_client,
            index="test-index",
            non_pipeline_indices=set(),
            reference="TUR1/1234/2024",
        )


def test_merge_without_none():
    """Test merge_without_none function with various None scenarios"""

    # Test 1: Both None
    result1 = merge_without_none({"a": None}, {"a": None})
    assert result1 == {"a": None}

    # Test 2: First None, second has value
    result2 = merge_without_none({"a": None}, {"a": "value2"})
    assert result2 == {"a": "value2"}

    # Test 3: First has value, second None
    result3 = merge_without_none({"a": "value1"}, {"a": None})
    assert result3 == {"a": "value1"}

    # Test 4: Both have values (dict2 takes precedence)
    result4 = merge_without_none({"a": "value1"}, {"a": "value2"})
    assert result4 == {"a": "value2"}

    # Test 5: Different keys
    result5 = merge_without_none(
        {"a": "value1", "b": None}, {"b": "value2", "c": "value3"}
    )
    assert result5 == {"a": "value1", "b": "value2", "c": "value3"}

    # Test 6: Complex case with mixed None values
    result6 = merge_without_none(
        {"a": None, "b": "keep1", "c": None, "d": "keep1"},
        {"a": "keep2", "b": None, "c": "keep2", "e": "new"},
    )
    expected = {"a": "keep2", "b": "keep1", "c": "keep2", "d": "keep1", "e": "new"}
    assert result6 == expected

    # Test 7: Empty dictionaries
    result7 = merge_without_none({}, {})
    assert result7 == {}

    # Test 8: One empty, one with values
    result8 = merge_without_none({}, {"a": "value", "b": None})
    assert result8 == {"a": "value", "b": None}
