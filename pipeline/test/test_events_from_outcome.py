import pytest
from datetime import datetime

from pipeline.transforms.events import events_from_outcome
from pipeline.transforms.model import EventType
from pipeline.document_classifier import DocumentType


def test_events_from_outcome_simple_acceptance():
    """Test events_from_outcome with a simple acceptance decision"""
    outcome = {
        "reference": "TUR1/1234(2024)",
        "last_updated": "2024-01-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {"acceptance_decision": "https://example.com/decision/123"},
    }

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
    outcome = {
        "reference": "TUR1/5678(2024)",
        "last_updated": "2024-03-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {
            "application_received": "https://example.com/app/456",
            "acceptance_decision": "https://example.com/acceptance/456",
            "recognition_decision": "https://example.com/recognition/456",
        },
    }

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
    outcome = {
        "reference": "TUR1/9012(2024)",
        "last_updated": "2024-03-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {
            "recognition_decision": "https://example.com/recognition/789",
            "acceptance_decision": "https://example.com/acceptance/789",
            "application_received": "https://example.com/app/789",
        },
    }

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
    outcome = {
        "reference": "TUR1/3456(2024)",
        "last_updated": "2024-02-15T10:30:00Z",
        "extracted_data": {"application_withdrawn": {}},
        "document_urls": {"application_withdrawn": "https://example.com/withdrawn/345"},
    }

    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should have 2 events: ApplicationReceived and ApplicationWithdrawn
    assert len(events) == 2

    # Both events should use the last_updated date as fallback
    assert events[0]["type"]["value"] == "application_received"
    assert events[0]["date"] == "2024-02-15"
    assert events[1]["type"]["value"] == "application_withdrawn"
    assert events[1]["date"] == "2024-02-15"


def test_events_from_outcome_application_withdrawn_with_previous_receipt():
    """Test events_from_outcome with application withdrawn but previous receipt exists"""
    outcome = {
        "reference": "TUR1/7890(2024)",
        "last_updated": "2024-02-15T10:30:00Z",
        "extracted_data": {
            "application_received": {"decision_date": "2023-12-01"},
            "application_withdrawn": {},
        },
        "document_urls": {
            "application_received": None,  # This triggers the escape hatch
            "application_withdrawn": "https://example.com/withdrawn/789",
        },
    }

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
    outcome = {
        "reference": "TUR1/1111(2024)",
        "last_updated": "2024-01-15T10:30:00Z",  # Earlier date
        "extracted_data": {
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
        "document_urls": {"acceptance_decision": "https://example.com/decision/111"},
    }

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
    outcome = {
        "reference": "TUR1/2222(2024)",
        "last_updated": "2024-08-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {
            "acceptance_decision": "https://example.com/acceptance/222",
            "form_of_ballot_decision": "https://example.com/ballot-form/222",
            "recognition_decision": "https://example.com/recognition/222",
        },
    }

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
    outcome = {
        "reference": "TUR1/3333(2024)",
        "last_updated": "2024-01-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {"acceptance_decision": "https://example.com/decision/333"},
    }

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
    outcome = {
        "reference": "TUR1/4444(2024)",
        "last_updated": "2024-02-15T10:30:00Z",
        "extracted_data": {
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
        "document_urls": {
            "acceptance_decision": "https://example.com/acceptance/444",
            "bargaining_unit_decision": "https://example.com/bargaining-unit/444",
        },
    }

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
    outcome = {
        "reference": "TUR1/5555(2024)",
        "last_updated": "2024-09-15T10:30:00Z",
        "extracted_data": {
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
                    "decision_type": "a decision on an unfair practice dispute during the access period",
                    "upheld": True,
                    "complainant": "Union",
                },
            },
        },
        "document_urls": {
            "acceptance_decision": "https://example.com/acceptance/555",
            "access_decision_or_dispute": "https://example.com/access/555",
        },
    }

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
    """Test events_from_outcome with a known bad outcome that should allow transform errors"""
    outcome = {
        "reference": "TUR1/1006(2017)",  # Known bad reference
        "last_updated": "2017-01-15T10:30:00Z",
        "extracted_data": {
            "acceptance_decision": {
                "decision_date": "2017-01-15",
                "success": True,
                "rejection_reasons": [],
                "application_date": "2016-12-01",
                "end_of_acceptance_period": "2017-01-10",
                "bargaining_unit": {
                    "description": "All workers at VWX Ltd",
                    "size_considered": True,
                    "size": 100,
                    "claimed_membership": 60,
                    "membership": 55,
                },
                "bargaining_unit_agreed": True,
                "petition_signatures": 65,
            }
        },
        "document_urls": {"acceptance_decision": "https://example.com/decision/1006"},
    }

    # This should not raise an exception due to the known bad reference
    events_builder = events_from_outcome(outcome)
    events = events_builder.dump_events()

    # Should still process normally
    assert len(events) == 2
    assert events[0]["type"]["value"] == "application_received"
    assert events[1]["type"]["value"] == "application_accepted"
