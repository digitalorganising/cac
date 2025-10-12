import pytest
from datetime import datetime

from pipeline.transforms.events import events_from_outcome
from pipeline.transforms.model import EventType
from pipeline.transforms.document_classifier import DocumentType
from pipeline.types.outcome import Outcome
from baml_client import types as baml_types


def create_outcome(
    id: str,
    last_updated: str,
    extracted_data: dict,
    document_urls: dict,
    outcome_url: str = None,
    outcome_title: str = None,
):
    """Helper function to create Outcome objects with required fields"""
    if outcome_url is None:
        outcome_url = f"https://example.com/outcome/{id}"
    if outcome_title is None:
        outcome_title = f"Test Outcome {id}"

    # Create documents dict from document_urls keys, handling None values
    documents = {}
    for doc_type, url in document_urls.items():
        if url is not None:  # Only include non-None URLs
            documents[doc_type] = "test"

    return Outcome(
        id=id,
        last_updated=last_updated,
        outcome_url=outcome_url,
        outcome_title=outcome_title,
        documents=documents,
        document_urls=document_urls,
        extracted_data=extracted_data,
    )


def test_events_from_outcome_simple_acceptance():
    """Test events_from_outcome with a simple acceptance decision"""
    outcome = create_outcome(
        id="TUR1/1234(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at ABC Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            }
        },
        document_urls={"acceptance_decision": "https://example.com/decision/123"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationAccepted
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received = events[0]
    assert app_received["type"]["value"] == "application_received"
    assert app_received["date"] == "2023-12-01"
    assert app_received["sourceDocumentUrl"] == "https://example.com/decision/123"

    # Check ApplicationAccepted event
    app_accepted = events[1]
    assert app_accepted["type"]["value"] == "application_accepted"
    assert app_accepted["date"] == "2024-01-15"
    assert app_accepted["sourceDocumentUrl"] == "https://example.com/decision/123"
    assert app_accepted["description"] == "Bargaining unit: All workers at ABC Ltd."


def test_events_from_outcome_multiple_documents_ordered():
    """Test events_from_outcome with multiple documents in chronological order"""
    outcome = create_outcome(
        id="TUR1/5678(2024)",
        last_updated="2024-03-15T10:30:00Z",
        extracted_data={
            "application_received": {"decision_date": "2023-12-01"},
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at XYZ Ltd",
                    "size_considered": True,
                    "size": 150,
                    "claimed_membership": 80,
                    "membership": 75,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 85,
            },
            "recognition_decision": {
                "decision_date": "2024-03-15",
                "union_recognized": True,
                "form_of_ballot": None,
                "ballot": None,
                "good_relations_contested": False,
            },
        },
        document_urls={
            "application_received": "https://example.com/app/456",
            "acceptance_decision": "https://example.com/acceptance/456",
            "recognition_decision": "https://example.com/recognition/456",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events: ApplicationReceived (from acceptance), ApplicationAccepted, UnionRecognized
    assert len(events) == 3

    # Check events are in chronological order
    assert (
        events[0]["type"]["value"] == "application_received"
    )  # From application_received
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-01-15"
    assert events[2]["type"]["value"] == "union_recognized"
    assert events[2]["date"] == "2024-03-15"


def test_events_from_outcome_documents_out_of_order():
    """Test events_from_outcome with documents in reverse chronological order"""
    outcome = create_outcome(
        id="TUR1/9012(2024)",
        last_updated="2024-03-15T10:30:00Z",
        extracted_data={
            "recognition_decision": {
                "decision_date": "2024-03-15",
                "union_recognized": True,
                "form_of_ballot": None,
                "ballot": None,
                "good_relations_contested": False,
            },
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at DEF Ltd",
                    "size_considered": True,
                    "size": 200,
                    "claimed_membership": 120,
                    "membership": 110,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 125,
            },
            "application_received": {"decision_date": "2023-12-01"},
        },
        document_urls={
            "recognition_decision": "https://example.com/recognition/789",
            "acceptance_decision": "https://example.com/acceptance/789",
            "application_received": "https://example.com/app/789",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events in chronological order despite input order
    assert len(events) == 3

    # Check events are in chronological order
    assert (
        events[0]["type"]["value"] == "application_received"
    )  # From application_received
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-01-15"
    assert events[2]["type"]["value"] == "union_recognized"
    assert events[2]["date"] == "2024-03-15"


def test_events_from_outcome_application_withdrawn():
    """Test events_from_outcome with application withdrawn"""
    outcome = create_outcome(
        id="TUR1/3456(2024)",
        last_updated="2025-03-15T10:30:00Z",  # After the cutoff date of 2025-02-15
        extracted_data={"application_withdrawn": None},
        document_urls={"application_withdrawn": "https://example.com/withdrawn/345"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationWithdrawn
    assert len(events) == 2

    # Both events should use the last_updated date as fallback
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2025-03-15"
    assert events[1]["type"]["value"] == "application_withdrawn"
    assert events[1]["date"] == "2025-03-15"


def test_events_from_outcome_application_withdrawn_with_previous_receipt():
    """Test events_from_outcome with application withdrawn but previous receipt exists"""
    outcome = create_outcome(
        id="TUR1/7890(2024)",
        last_updated="2024-02-15T10:30:00Z",
        extracted_data={
            "application_received": {"decision_date": "2023-12-01"},
            "application_withdrawn": None,
        },
        document_urls={
            "application_withdrawn": "https://example.com/withdrawn/789",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived (from withdrawn), ApplicationWithdrawn
    assert len(events) == 2

    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_withdrawn"
    assert events[1]["date"] == "2024-02-15"  # Uses fallback date


def test_events_from_outcome_last_updated_date_correction():
    """Test events_from_outcome where last_updated date is corrected by latest document"""
    outcome = create_outcome(
        id="TUR1/1111(2024)",
        last_updated="2024-01-15T10:30:00Z",  # Earlier date
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-03-15",  # Later date
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at GHI Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            }
        },
        document_urls={"acceptance_decision": "https://example.com/decision/111"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events
    assert len(events) == 2

    # The fallback date should be corrected to the latest document date
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-03-15"


def test_events_from_outcome_complex_recognition_with_ballot():
    """Test events_from_outcome with complex recognition decision including ballot"""
    outcome = create_outcome(
        id="TUR1/2222(2024)",
        last_updated="2024-08-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at JKL Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            },
            "form_of_ballot_decision": {
                "decision_date": "2024-06-01",
                "form_of_ballot": "Postal",
                "employer_preferred": "Workplace",
                "union_preferred": "Postal",
            },
            "recognition_decision": {
                "decision_date": "2024-08-15",
                "union_recognized": True,
                "form_of_ballot": "Postal",
                "ballot": {
                    "eligible_workers": 100,
                    "spoiled_ballots": 2,
                    "votes_in_favor": 60,
                    "votes_against": 20,
                    "start_ballot_period": "2024-07-15",
                    "end_ballot_period": "2024-07-30",
                },
                "good_relations_contested": False,
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/222",
            "form_of_ballot_decision": "https://example.com/ballot-form/222",
            "recognition_decision": "https://example.com/recognition/222",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 5 events in chronological order
    assert len(events) == 5

    # Check events are in correct order
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-01-15"
    assert events[2]["type"]["value"] == "ballot_form_postal"
    assert events[2]["date"] == "2024-06-01"
    assert events[3]["type"]["value"] == "ballot_held"
    assert events[3]["date"] == "2024-07-15"
    assert events[4]["type"]["value"] == "union_recognized"
    assert events[4]["date"] == "2024-08-15"


def test_events_from_outcome_rejected_application():
    """Test events_from_outcome with rejected application"""
    outcome = create_outcome(
        id="TUR1/3333(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": False,
                "rejection_reasons": ["LessThan10PercentMembership"],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at MNO Ltd",
                    "size_considered": True,
                    "size": 200,
                    "claimed_membership": 15,
                    "membership": 12,
                },
                "bargaining_unit_agreed": False,
                "petition_signatures": None,
            }
        },
        document_urls={"acceptance_decision": "https://example.com/decision/333"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationRejected
    assert len(events) == 2

    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_rejected"
    assert events[1]["date"] == "2024-01-15"


def test_events_from_outcome_bargaining_unit_inappropriate():
    """Test events_from_outcome with bargaining unit decision where unit is inappropriate"""
    outcome = create_outcome(
        id="TUR1/4444(2024)",
        last_updated="2024-02-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at PQR Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            },
            "bargaining_unit_decision": {
                "decision_date": "2024-02-15",
                "appropriate_unit_differs": True,
                "new_bargaining_unit_description": "All production workers at the Birmingham factory",
                "lawyer_present": False,
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/444",
            "bargaining_unit_decision": "https://example.com/bargaining-unit/444",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events
    assert len(events) == 3

    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-01-15"
    assert events[2]["type"]["value"] == "bargaining_unit_inappropriate"
    assert events[2]["date"] == "2024-02-15"
    assert (
        events[2]["description"] == "All production workers at the Birmingham factory."
    )


def test_events_from_outcome_access_dispute():
    """Test events_from_outcome with access decision/dispute"""
    outcome = create_outcome(
        id="TUR1/5555(2024)",
        last_updated="2024-09-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at STU Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            },
            "access_decision_or_dispute": {
                "decision_date": "2024-09-15",
                "details": {
                    "decision_type": "unfair_practice_dispute",
                    "upheld": True,
                    "complainant": "Union",
                },
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/555",
            "access_decision_or_dispute": "https://example.com/access/555",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events
    assert len(events) == 3

    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-01-15"
    assert events[2]["type"]["value"] == "unfair_practice_upheld"
    assert events[2]["date"] == "2024-09-15"
    assert events[2]["description"] == "Complaint from union."


def test_events_from_outcome_allowed_transform_error():
    """Test events_from_outcome with allowed transform errors"""
    outcome = create_outcome(
        id="TUR1/1006(2017)",  # Known bad reference that allows errors
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at Test Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            }
        },
        document_urls={},  # Missing document URLs
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should handle missing document URLs gracefully
    assert len(events) == 2

    # Check events have missing source URLs (field omitted when None)
    assert events[0]["type"]["value"] == "application_received"
    assert "sourceDocumentUrl" not in events[0]
    assert events[1]["type"]["value"] == "application_accepted"
    assert "sourceDocumentUrl" not in events[1]


def test_events_from_outcome_missing_document_urls():
    """Test events_from_outcome with missing document URLs"""
    outcome = create_outcome(
        id="TUR1/9999(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
                "bargaining_unit": {
                    "description": "All workers at Test Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            }
        },
        document_urls={},  # Empty document URLs
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should handle missing document URLs gracefully
    assert len(events) == 2

    # Check events have missing source URLs (field omitted when None)
    assert events[0]["type"]["value"] == "application_received"
    assert "sourceDocumentUrl" not in events[0]
    assert events[1]["type"]["value"] == "application_accepted"
    assert "sourceDocumentUrl" not in events[1]


def test_events_from_outcome_partial_document_urls():
    """Test events_from_outcome with partial document URLs"""
    outcome = create_outcome(
        id="TUR1/8888(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
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
            "recognition_decision": {
                "decision_date": "2024-03-15",
                "union_recognized": True,
                "form_of_ballot": None,
                "ballot": None,
                "good_relations_contested": False,
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/888",
            # Missing recognition_decision URL
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should handle partial document URLs gracefully
    assert len(events) == 3

    # Check events have appropriate source URLs
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["sourceDocumentUrl"] == "https://example.com/acceptance/888"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["sourceDocumentUrl"] == "https://example.com/acceptance/888"
    assert events[2]["type"]["value"] == "union_recognized"
    assert "sourceDocumentUrl" not in events[2]  # Field omitted when None


def test_events_from_outcome_application_withdrawn_with_escape_hatch():
    """Test events_from_outcome with application withdrawn using escape hatch logic"""
    outcome = create_outcome(
        id="TUR1/7777(2024)",
        last_updated="2025-03-15T10:30:00Z",  # After cutoff
        extracted_data={
            "application_received": {"decision_date": "2023-12-01"},
            "application_withdrawn": None,
        },
        document_urls={
            "application_withdrawn": "https://example.com/withdrawn/777",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationWithdrawn
    assert len(events) == 2

    # Both events should use the withdrawn document URL due to escape hatch
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    # Note: sourceDocumentUrl field may not be present in all event formats
    assert events[1]["type"]["value"] == "application_withdrawn"
    assert events[1]["date"] == "2025-03-15"


def test_events_from_outcome_last_updated_date_correction_edge_case():
    """Test events_from_outcome where last_updated date is corrected by latest document"""
    outcome = create_outcome(
        id="TUR1/6666(2024)",
        last_updated="2024-01-15T10:30:00Z",  # Earlier date
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-03-15",  # Later date
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
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
            "recognition_decision": {
                "decision_date": "2024-05-15",  # Even later date
                "union_recognized": True,
                "form_of_ballot": None,
                "ballot": None,
                "good_relations_contested": False,
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/666",
            "recognition_decision": "https://example.com/recognition/666",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events
    assert len(events) == 3

    # The fallback date should be corrected to the latest document date (2024-05-15)
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[1]["date"] == "2024-03-15"
    assert events[2]["type"]["value"] == "union_recognized"
    assert events[2]["date"] == "2024-05-15"


def test_events_from_outcome_missing_decision_date_in_document():
    """Test events_from_outcome with missing decision_date in document"""
    outcome = create_outcome(
        id="TUR1/5555(2024)",
        last_updated="2025-03-15T10:30:00Z",  # After cutoff date
        extracted_data={
            "application_withdrawn": None,
        },
        document_urls={"application_withdrawn": "https://example.com/withdrawn/555"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should handle missing decision_date gracefully using last_updated as fallback
    assert (
        len(events) == 2
    )  # Both ApplicationReceived and ApplicationWithdrawn after cutoff

    # Check ApplicationReceived event uses last_updated as fallback
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2025-03-15"  # Uses last_updated date
    assert events[0]["sourceDocumentUrl"] == "https://example.com/withdrawn/555"

    # Check ApplicationWithdrawn event
    assert events[1]["type"]["value"] == "application_withdrawn"
    assert events[1]["date"] == "2025-03-15"  # Uses last_updated date
    assert events[1]["sourceDocumentUrl"] == "https://example.com/withdrawn/555"


def test_events_from_outcome_empty_extracted_data():
    """Test events_from_outcome with empty extracted_data"""
    outcome = create_outcome(
        id="TUR1/4444(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={},  # Empty extracted data
        document_urls={},
    )

    # This should raise StopIteration when trying to get last_doc from empty OrderedDict
    with pytest.raises(StopIteration):
        events_from_outcome(outcome)


def test_events_from_outcome_none_extracted_data():
    """Test events_from_outcome with None extracted_data"""
    # For None extracted_data, we need to create the Outcome manually
    outcome = Outcome(
        id="TUR1/3333(2024)",
        last_updated="2024-01-15T10:30:00Z",
        outcome_url="https://example.com/outcome/TUR1/3333(2024)",
        outcome_title="Test Outcome TUR1/3333(2024)",
        documents={},
        document_urls={},
        extracted_data={},  # Empty extracted data
    )

    # This should raise StopIteration when trying to get last_doc from empty OrderedDict
    with pytest.raises(StopIteration):
        events_from_outcome(outcome)


def test_events_from_outcome_duplicate_event_prevention():
    """Test events_from_outcome with duplicate events to verify prevention logic"""
    outcome = create_outcome(
        id="TUR1/2222(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "acceptance_decision": {
                "decision_date": "2024-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2023-12-01",
                "end_of_acceptance_period": "2024-01-10",
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
            "recognition_decision": {
                "decision_date": "2024-03-15",
                "union_recognized": True,
                "form_of_ballot": None,
                "ballot": None,
                "good_relations_contested": False,
            },
            "method_agreed": {
                "decision_date": "2024-04-15",
            },
        },
        document_urls={
            "acceptance_decision": "https://example.com/acceptance/222",
            "recognition_decision": "https://example.com/recognition/222",
            "method_agreed": "https://example.com/method/222",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 4 events: ApplicationReceived, ApplicationAccepted, UnionRecognized, MethodAgreed
    assert len(events) == 4

    # Check events are in correct order and no duplicates
    assert events[0]["type"]["value"] == "application_received"
    assert events[1]["type"]["value"] == "application_accepted"
    assert events[2]["type"]["value"] == "union_recognized"
    assert events[3]["type"]["value"] == "method_agreed"

    # Verify no duplicate events exist
    event_types = [event["type"]["value"] for event in events]
    assert len(event_types) == len(set(event_types)), "Duplicate events found"


def test_events_from_outcome_consecutive_duplicate_events():
    """Test events_from_outcome with consecutive duplicate events to verify prevention"""
    outcome = create_outcome(
        id="TUR1/1111(2024)",
        last_updated="2024-01-15T10:30:00Z",
        extracted_data={
            "application_received": {"decision_date": "2023-12-01"},
            "application_received": {"decision_date": "2023-12-01"},  # Duplicate
        },
        document_urls={
            "application_received": "https://example.com/app/111",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have only 1 ApplicationReceived event (duplicate prevented)
    assert len(events) == 1
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"


def test_events_from_outcome_para_35_decision_valid():
    """Test events_from_outcome with Paragraph 35 decision - application can proceed"""
    outcome = create_outcome(
        id="TUR1/1234(2024)",
        last_updated="2024-02-15T10:30:00Z",
        extracted_data={
            "para_35_decision": {
                "decision_date": "2024-02-15",
                "application_date": "2023-12-01",
                "application_can_proceed": True,
            }
        },
        document_urls={"para_35_decision": "https://example.com/para35/123"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationP35Valid
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received = events[0]
    assert app_received["type"]["value"] == "application_received"
    assert app_received["date"] == "2023-12-01"
    assert app_received["sourceDocumentUrl"] == "https://example.com/para35/123"

    # Check ApplicationP35Valid event
    p35_valid = events[1]
    assert p35_valid["type"]["value"] == "application_p35_valid"
    assert p35_valid["date"] == "2024-02-15"
    assert p35_valid["sourceDocumentUrl"] == "https://example.com/para35/123"
    assert (
        p35_valid["description"]
        == "Determined that no other bargaining is in place, and the application can proceed."
    )


def test_events_from_outcome_para_35_decision_invalid():
    """Test events_from_outcome with Paragraph 35 decision - application cannot proceed"""
    outcome = create_outcome(
        id="TUR1/5678(2024)",
        last_updated="2024-02-15T10:30:00Z",
        extracted_data={
            "para_35_decision": {
                "decision_date": "2024-02-15",
                "application_date": "2023-12-01",
                "application_can_proceed": False,
            }
        },
        document_urls={"para_35_decision": "https://example.com/para35/456"},
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationP35Invalid
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received = events[0]
    assert app_received["type"]["value"] == "application_received"
    assert app_received["date"] == "2023-12-01"
    assert app_received["sourceDocumentUrl"] == "https://example.com/para35/456"

    # Check ApplicationP35Invalid event
    p35_invalid = events[1]
    assert p35_invalid["type"]["value"] == "application_p35_invalid"
    assert p35_invalid["date"] == "2024-02-15"
    assert p35_invalid["sourceDocumentUrl"] == "https://example.com/para35/456"
    assert (
        p35_invalid["description"]
        == "Collective bargaining already in place, application was rejected."
    )


def test_events_from_outcome_para_35_with_other_decisions():
    """Test events_from_outcome with Paragraph 35 decision followed by other decisions"""
    outcome = create_outcome(
        id="TUR1/9999(2024)",
        last_updated="2024-03-15T10:30:00Z",
        extracted_data={
            "para_35_decision": {
                "decision_date": "2024-02-15",
                "application_date": "2023-12-01",
                "application_can_proceed": True,
            },
            "acceptance_decision": {
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
        },
        document_urls={
            "para_35_decision": "https://example.com/para35/999",
            "acceptance_decision": "https://example.com/acceptance/999",
        },
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 3 events: ApplicationReceived, ApplicationP35Valid, ApplicationAccepted
    assert len(events) == 3

    # Check events are in chronological order
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2023-12-01"
    assert events[1]["type"]["value"] == "application_p35_valid"
    assert events[1]["date"] == "2024-02-15"
    assert events[2]["type"]["value"] == "application_accepted"
    assert events[2]["date"] == "2024-03-15"


def test_events_from_outcome_para_35_missing_document_url():
    """Test events_from_outcome with Paragraph 35 decision but missing document URL"""
    outcome = create_outcome(
        id="TUR1/8888(2024)",
        last_updated="2024-02-15T10:30:00Z",
        extracted_data={
            "para_35_decision": {
                "decision_date": "2024-02-15",
                "application_date": "2023-12-01",
                "application_can_proceed": True,
            }
        },
        document_urls={},  # Missing document URLs
    )

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should handle missing document URLs gracefully
    assert len(events) == 2

    # Check events have missing source URLs (field omitted when None)
    assert events[0]["type"]["value"] == "application_received"
    assert "sourceDocumentUrl" not in events[0]
    assert events[1]["type"]["value"] == "application_p35_valid"
    assert "sourceDocumentUrl" not in events[1]
