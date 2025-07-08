import pytest
from datetime import datetime

from pipeline.transforms.events_from_decision import events_from_decision, Decision
from pipeline.transforms.model import EventType
from pipeline.transforms.document_classifier import DocumentType


def test_events_from_decision_acceptance_decision_success():
    """Test events_from_decision with a successful acceptance decision"""
    # Sample acceptance decision data
    acceptance_decision_doc = {
        "decision_date": "2024-01-15",
        "success": True,
        "rejection_reasons": [],
        "application_date": "2023-12-01",
        "end_of_acceptance_period": "2024-01-10",
        "bargaining_unit": {
            "description": "All workers employed by ABC Ltd at their Manchester site",
            "size_considered": True,
            "size": 150,
            "claimed_membership": 80,
            "membership": 75,
        },
        "bargaining_unit_agreed": True,
        "petition_signatures": 85,
    }

    source_url = "https://example.com/decision/123"
    decision = Decision[DocumentType.acceptance_decision](
        acceptance_decision_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 2 events: ApplicationReceived and ApplicationAccepted
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == datetime(2023, 12, 1).date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None

    # Check ApplicationAccepted event
    app_accepted_event = events[1]
    assert app_accepted_event.type == EventType.ApplicationAccepted
    assert app_accepted_event.date == datetime(2024, 1, 15).date()
    assert str(app_accepted_event.source_document_url) == source_url
    assert (
        app_accepted_event.description
        == "Bargaining unit: All workers employed by ABC Ltd at their Manchester site."
    )


def test_events_from_decision_acceptance_decision_rejected():
    """Test events_from_decision with a rejected acceptance decision"""
    # Sample rejected acceptance decision data
    acceptance_decision_doc = {
        "decision_date": "2024-01-15",
        "success": False,
        "rejection_reasons": ["LessThan10PercentMembership"],
        "application_date": "2023-12-01",
        "end_of_acceptance_period": "2024-01-10",
        "bargaining_unit": {
            "description": "All workers employed by XYZ Ltd at their London site",
            "size_considered": True,
            "size": 200,
            "claimed_membership": 15,
            "membership": 12,
        },
        "bargaining_unit_agreed": False,
        "petition_signatures": None,
    }

    source_url = "https://example.com/decision/456"
    decision = Decision[DocumentType.acceptance_decision](
        acceptance_decision_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 2 events: ApplicationReceived and ApplicationRejected
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == datetime(2023, 12, 1).date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None

    # Check ApplicationRejected event
    app_rejected_event = events[1]
    assert app_rejected_event.type == EventType.ApplicationRejected
    assert app_rejected_event.date == datetime(2024, 1, 15).date()
    assert str(app_rejected_event.source_document_url) == source_url
    assert (
        app_rejected_event.description
        == "Bargaining unit: All workers employed by XYZ Ltd at their London site."
    )


def test_events_from_decision_application_received():
    """Test events_from_decision with an application received document"""
    application_received_doc = {"decision_date": "2023-12-01"}

    source_url = "https://example.com/application/789"
    decision = Decision[DocumentType.application_received](
        application_received_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: ApplicationReceived
    assert len(events) == 1

    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == datetime(2023, 12, 1).date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None


def test_events_from_decision_application_withdrawn():
    """Test events_from_decision with an application withdrawn document"""
    application_withdrawn_doc = {}  # No specific data needed

    source_url = "https://example.com/withdrawn/101"
    fallback_date = datetime(2025, 3, 15)  # After the cutoff date of 2025-02-15
    decision = Decision[DocumentType.application_withdrawn](
        application_withdrawn_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 2 events: ApplicationReceived and ApplicationWithdrawn
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == fallback_date.date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[1]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_bargaining_unit_decision_appropriate():
    """Test events_from_decision with a bargaining unit decision where unit is appropriate"""
    bargaining_unit_doc = {
        "decision_date": "2024-02-01",
        "appropriate_unit_differs": False,
        "new_bargaining_unit_description": None,
        "lawyer_present": True,
    }

    source_url = "https://example.com/bargaining-unit/202"
    decision = Decision[DocumentType.bargaining_unit_decision](
        bargaining_unit_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BargainingUnitAppropriate
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BargainingUnitAppropriate
    assert event.date == datetime(2024, 2, 1).date()
    assert str(event.source_document_url) == source_url
    assert (
        event.description
        == "The original bargaining unit from the application was determined by the CAC to be appropriate."
    )


def test_events_from_decision_bargaining_unit_decision_inappropriate():
    """Test events_from_decision with a bargaining unit decision where unit is inappropriate"""
    bargaining_unit_doc = {
        "decision_date": "2024-02-01",
        "appropriate_unit_differs": True,
        "new_bargaining_unit_description": "All production workers at the Birmingham factory",
        "lawyer_present": False,
    }

    source_url = "https://example.com/bargaining-unit/203"
    decision = Decision[DocumentType.bargaining_unit_decision](
        bargaining_unit_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BargainingUnitInappropriate
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BargainingUnitInappropriate
    assert event.date == datetime(2024, 2, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "All production workers at the Birmingham factory."


def test_events_from_decision_bargaining_decision():
    """Test events_from_decision with a bargaining decision"""
    bargaining_doc = {"decision_date": "2024-03-01"}

    source_url = "https://example.com/bargaining/304"
    decision = Decision[DocumentType.bargaining_decision](bargaining_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: MethodDecision
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.MethodDecision
    assert event.date == datetime(2024, 3, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description is None


def test_events_from_decision_form_of_ballot_decision_postal():
    """Test events_from_decision with a form of ballot decision - postal"""
    form_of_ballot_doc = {
        "decision_date": "2024-04-01",
        "form_of_ballot": "Postal",
        "employer_preferred": "Workplace",
        "union_preferred": "Postal",
    }

    source_url = "https://example.com/ballot-form/405"
    decision = Decision[DocumentType.form_of_ballot_decision](
        form_of_ballot_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BallotFormPostal
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BallotFormPostal
    assert event.date == datetime(2024, 4, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "Employer preferred workplace; union preferred postal."


def test_events_from_decision_form_of_ballot_decision_workplace():
    """Test events_from_decision with a form of ballot decision - workplace"""
    form_of_ballot_doc = {
        "decision_date": "2024-04-01",
        "form_of_ballot": "Workplace",
        "employer_preferred": "Workplace",
        "union_preferred": "Postal",
    }

    source_url = "https://example.com/ballot-form/406"
    decision = Decision[DocumentType.form_of_ballot_decision](
        form_of_ballot_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BallotFormWorkplace
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BallotFormWorkplace
    assert event.date == datetime(2024, 4, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "Employer preferred workplace; union preferred postal."


def test_events_from_decision_form_of_ballot_decision_combination():
    """Test events_from_decision with a form of ballot decision - combination"""
    form_of_ballot_doc = {
        "decision_date": "2024-04-01",
        "form_of_ballot": "Combination",
        "employer_preferred": "Workplace",
        "union_preferred": "Postal",
    }

    source_url = "https://example.com/ballot-form/407"
    decision = Decision[DocumentType.form_of_ballot_decision](
        form_of_ballot_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BallotFormCombination
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BallotFormCombination
    assert event.date == datetime(2024, 4, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "Employer preferred workplace; union preferred postal."


def test_events_from_decision_whether_to_ballot_decision_ballot_required():
    """Test events_from_decision with a whether to ballot decision - ballot required"""
    whether_to_ballot_doc = {
        "decision_date": "2024-05-01",
        "decision_to_ballot": True,
        "majority_membership": True,
        "qualifying_conditions": ["GoodIndustrialRelations", "EvidenceMembersOpposed"],
    }

    source_url = "https://example.com/whether-ballot/508"
    decision = Decision[DocumentType.whether_to_ballot_decision](
        whether_to_ballot_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BallotRequirementDecided
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BallotRequirementDecided
    assert event.date == datetime(2024, 5, 1).date()
    assert str(event.source_document_url) == source_url
    assert (
        event.description
        == "For the reasons of it being in the interests of good industrial relations; evidence from members of the union that they are opposed to it conducting collective bargaining."
    )


def test_events_from_decision_whether_to_ballot_decision_no_ballot():
    """Test events_from_decision with a whether to ballot decision - no ballot required"""
    whether_to_ballot_doc = {
        "decision_date": "2024-05-01",
        "decision_to_ballot": False,
        "majority_membership": True,
        "qualifying_conditions": [],
    }

    source_url = "https://example.com/whether-ballot/509"
    decision = Decision[DocumentType.whether_to_ballot_decision](
        whether_to_ballot_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: BallotNotRequired
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.BallotNotRequired
    assert event.date == datetime(2024, 5, 1).date()
    assert str(event.source_document_url) == source_url
    assert (
        event.description
        == "There was a majority membership and no other reasons to ballot were identified."
    )


def test_events_from_decision_validity_decision_invalid():
    """Test events_from_decision with a validity decision - invalid"""
    validity_doc = {
        "decision_date": "2024-06-01",
        "valid": False,
        "rejection_reasons": ["SomeOtherReason"],
        "new_bargaining_unit": {
            "description": "All workers at the new site",
            "size_considered": True,
            "size": 100,
            "claimed_membership": 50,
            "membership": 45,
        },
        "petition_signatures": 55,
    }

    source_url = "https://example.com/validity/610"
    decision = Decision[DocumentType.validity_decision](validity_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: ApplicationRejected
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.ApplicationRejected
    assert event.date == datetime(2024, 6, 1).date()
    assert str(event.source_document_url) == source_url
    assert (
        event.description
        == "The application was found no longer to be valid after the change of bargaining unit."
    )


def test_events_from_decision_validity_decision_valid():
    """Test events_from_decision with a validity decision - valid"""
    validity_doc = {
        "decision_date": "2024-06-01",
        "valid": True,
        "rejection_reasons": [],
        "new_bargaining_unit": {
            "description": "All workers at the site",
            "size_considered": True,
            "size": 100,
            "claimed_membership": 60,
            "membership": 55,
        },
        "petition_signatures": 65,
    }

    source_url = "https://example.com/validity/611"
    decision = Decision[DocumentType.validity_decision](validity_doc, source_url)

    events = events_from_decision(decision)

    # Should return 0 events when valid
    assert len(events) == 0


def test_events_from_decision_case_closure():
    """Test events_from_decision with a case closure document"""
    case_closure_doc = {"decision_date": "2024-07-01"}

    source_url = "https://example.com/closure/712"
    decision = Decision[DocumentType.case_closure](case_closure_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: CaseClosed
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.CaseClosed
    assert event.date == datetime(2024, 7, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description is None


def test_events_from_decision_recognition_decision_recognized_with_ballot():
    """Test events_from_decision with a recognition decision - union recognized with ballot"""
    recognition_doc = {
        "decision_date": "2024-08-01",
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
    }

    source_url = "https://example.com/recognition/813"
    decision = Decision[DocumentType.recognition_decision](recognition_doc, source_url)

    events = events_from_decision(decision)

    # Should return 2 events: BallotHeld and UnionRecognized
    assert len(events) == 2

    # Check BallotHeld event
    ballot_event = events[0]
    assert ballot_event.type == EventType.BallotHeld
    assert ballot_event.date == datetime(2024, 7, 15).date()
    assert str(ballot_event.source_document_url) == source_url
    assert (
        ballot_event.description
        == "A postal ballot with 100 eligible workers ran from 2024-07-15 to 2024-07-30."
    )

    # Check UnionRecognized event
    recognition_event = events[1]
    assert recognition_event.type == EventType.UnionRecognized
    assert recognition_event.date == datetime(2024, 8, 1).date()
    assert str(recognition_event.source_document_url) == source_url
    assert recognition_event.description == "Workers voted to recognise the union."


def test_events_from_decision_recognition_decision_not_recognized_with_ballot():
    """Test events_from_decision with a recognition decision - union not recognized with ballot"""
    recognition_doc = {
        "decision_date": "2024-08-01",
        "union_recognized": False,
        "form_of_ballot": "Workplace",
        "ballot": {
            "eligible_workers": 100,
            "spoiled_ballots": 1,
            "votes_in_favor": 30,
            "votes_against": 50,
            "start_ballot_period": "2024-07-15",
            "end_ballot_period": "2024-07-30",
        },
        "good_relations_contested": False,
    }

    source_url = "https://example.com/recognition/814"
    decision = Decision[DocumentType.recognition_decision](recognition_doc, source_url)

    events = events_from_decision(decision)

    # Should return 2 events: BallotHeld and UnionNotRecognized
    assert len(events) == 2

    # Check BallotHeld event
    ballot_event = events[0]
    assert ballot_event.type == EventType.BallotHeld
    assert ballot_event.date == datetime(2024, 7, 15).date()
    assert str(ballot_event.source_document_url) == source_url
    assert (
        ballot_event.description
        == "A workplace ballot with 100 eligible workers ran from 2024-07-15 to 2024-07-30."
    )

    # Check UnionNotRecognized event
    recognition_event = events[1]
    assert recognition_event.type == EventType.UnionNotRecognized
    assert recognition_event.date == datetime(2024, 8, 1).date()
    assert str(recognition_event.source_document_url) == source_url
    assert recognition_event.description == "Workers voted against recognition."


def test_events_from_decision_recognition_decision_recognized_no_ballot():
    """Test events_from_decision with a recognition decision - union recognized without ballot"""
    recognition_doc = {
        "decision_date": "2024-08-01",
        "union_recognized": True,
        "form_of_ballot": None,
        "ballot": None,
        "good_relations_contested": False,
    }

    source_url = "https://example.com/recognition/815"
    decision = Decision[DocumentType.recognition_decision](recognition_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: UnionRecognized
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.UnionRecognized
    assert event.date == datetime(2024, 8, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "No ballot was held."


def test_events_from_decision_access_decision_or_dispute_unfair_practice_upheld():
    """Test events_from_decision with an access decision - unfair practice upheld"""
    access_doc = {
        "decision_date": "2024-09-01",
        "details": {
            "decision_type": "a decision on an unfair practice dispute during the access period",
            "upheld": True,
            "complainant": "Union",
        },
    }

    source_url = "https://example.com/access/916"
    decision = Decision[DocumentType.access_decision_or_dispute](access_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: UnfairPracticeUpheld
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.UnfairPracticeUpheld
    assert event.date == datetime(2024, 9, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "Complaint from union."


def test_events_from_decision_access_decision_or_dispute_unfair_practice_not_upheld():
    """Test events_from_decision with an access decision - unfair practice not upheld"""
    access_doc = {
        "decision_date": "2024-09-01",
        "details": {
            "decision_type": "a decision on an unfair practice dispute during the access period",
            "upheld": False,
            "complainant": "Employer",
        },
    }

    source_url = "https://example.com/access/917"
    decision = Decision[DocumentType.access_decision_or_dispute](access_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: UnfairPracticeNotUpheld
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.UnfairPracticeNotUpheld
    assert event.date == datetime(2024, 9, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description == "Complaint from employer."


def test_events_from_decision_access_decision_or_dispute_access_arrangement():
    """Test events_from_decision with an access decision - access arrangement"""
    access_doc = {
        "decision_date": "2024-09-01",
        "details": {
            "decision_type": "a decision on access arrangements in advance of a ballot, or during it with a pause",
            "favors": "Union",
            "description": "Union granted access to workplace noticeboards and email distribution lists",
        },
    }

    source_url = "https://example.com/access/918"
    decision = Decision[DocumentType.access_decision_or_dispute](access_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: AccessArrangement
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.AccessArrangement
    assert event.date == datetime(2024, 9, 1).date()
    assert str(event.source_document_url) == source_url
    assert (
        event.description
        == "Union granted access to workplace noticeboards and email distribution lists."
    )


def test_events_from_decision_method_agreed():
    """Test events_from_decision with a method agreed document"""
    method_agreed_doc = {"decision_date": "2024-10-01"}

    source_url = "https://example.com/method/1019"
    decision = Decision[DocumentType.method_agreed](method_agreed_doc, source_url)

    events = events_from_decision(decision)

    # Should return 1 event: MethodAgreed
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.MethodAgreed
    assert event.date == datetime(2024, 10, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description is None


def test_events_from_decision_nullification_decision():
    """Test events_from_decision with a nullification decision"""
    nullification_doc = {"decision_date": "2024-11-01"}

    source_url = "https://example.com/nullification/1120"
    decision = Decision[DocumentType.nullification_decision](
        nullification_doc, source_url
    )

    events = events_from_decision(decision)

    # Should return 1 event: ApplicationRejected
    assert len(events) == 1

    event = events[0]
    assert event.type == EventType.ApplicationRejected
    assert event.date == datetime(2024, 11, 1).date()
    assert str(event.source_document_url) == source_url
    assert event.description is None


def test_events_from_decision_generic_doc():
    """Test events_from_decision with a generic document type"""
    generic_doc = {"decision_date": "2024-01-01"}

    source_url = "https://example.com/generic/999"
    decision = Decision(generic_doc, source_url)

    events = events_from_decision(decision)

    # Should return empty list for unknown document type
    assert len(events) == 0


def test_events_from_decision_null_source_url():
    """Test events_from_decision with null source URL"""
    acceptance_doc = {
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

    decision = Decision[DocumentType.acceptance_decision](acceptance_doc, None)

    events = events_from_decision(decision)

    # Should return 2 events even with null source URL
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == datetime(2023, 12, 1).date()
    assert app_received_event.source_document_url is None
    assert app_received_event.description is None

    # Check ApplicationAccepted event
    app_accepted_event = events[1]
    assert app_accepted_event.type == EventType.ApplicationAccepted
    assert app_accepted_event.date == datetime(2024, 1, 15).date()
    assert app_accepted_event.source_document_url is None
    assert app_accepted_event.description == "Bargaining unit: All workers at Test Ltd."


def test_events_from_decision_missing_decision_date():
    """Test events_from_decision with missing decision_date in document"""
    # Use application_withdrawn which doesn't require decision_date
    application_withdrawn_doc = {}  # No decision_date

    source_url = "https://example.com/withdrawn/999"
    fallback_date = datetime(2024, 1, 15)
    decision = Decision[DocumentType.application_withdrawn](
        application_withdrawn_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 1 event using fallback date
    assert len(events) == 1

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[0]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_application_withdrawn_before_cutoff():
    """Test events_from_decision with application withdrawn before cutoff date"""
    application_withdrawn_doc = {}  # No specific data needed

    source_url = "https://example.com/withdrawn/101"
    fallback_date = datetime(2024, 1, 15)  # Before the cutoff date of 2025-02-15
    decision = Decision[DocumentType.application_withdrawn](
        application_withdrawn_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return only 1 event: ApplicationWithdrawn (no ApplicationReceived before cutoff)
    assert len(events) == 1

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[0]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_application_withdrawn_after_cutoff():
    """Test events_from_decision with application withdrawn after cutoff date"""
    application_withdrawn_doc = {}  # No specific data needed

    source_url = "https://example.com/withdrawn/102"
    fallback_date = datetime(2025, 3, 15)  # After the cutoff date of 2025-02-15
    decision = Decision[DocumentType.application_withdrawn](
        application_withdrawn_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 2 events: ApplicationReceived and ApplicationWithdrawn (after cutoff)
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == fallback_date.date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[1]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_application_withdrawn_exactly_at_cutoff():
    """Test events_from_decision with application withdrawn exactly at cutoff date"""
    application_withdrawn_doc = {}  # No specific data needed

    source_url = "https://example.com/withdrawn/103"
    fallback_date = datetime(2025, 2, 15)  # Exactly at the cutoff date of 2025-02-15
    decision = Decision[DocumentType.application_withdrawn](
        application_withdrawn_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 2 events: ApplicationReceived and ApplicationWithdrawn (at cutoff)
    assert len(events) == 2

    # Check ApplicationReceived event
    app_received_event = events[0]
    assert app_received_event.type == EventType.ApplicationReceived
    assert app_received_event.date == fallback_date.date()
    assert str(app_received_event.source_document_url) == source_url
    assert app_received_event.description is None

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[1]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_recognition_decision_lowercase_ballot_descriptions():
    """Test events_from_decision with recognition decision to verify lowercase ballot descriptions"""
    recognition_doc = {
        "decision_date": "2024-08-01",
        "union_recognized": True,
        "form_of_ballot": "Postal",  # Should become "postal" in description
        "ballot": {
            "eligible_workers": 100,
            "spoiled_ballots": 2,
            "votes_in_favor": 60,
            "votes_against": 20,
            "start_ballot_period": "2024-07-15",
            "end_ballot_period": "2024-07-30",
        },
        "good_relations_contested": False,
    }

    source_url = "https://example.com/recognition/999"
    decision = Decision[DocumentType.recognition_decision](recognition_doc, source_url)

    events = events_from_decision(decision)

    # Should return 2 events: BallotHeld and UnionRecognized
    assert len(events) == 2

    # Check BallotHeld event has lowercase description
    ballot_event = events[0]
    assert ballot_event.type == EventType.BallotHeld
    assert ballot_event.date == datetime(2024, 7, 15).date()
    assert str(ballot_event.source_document_url) == source_url
    assert (
        ballot_event.description
        == "A postal ballot with 100 eligible workers ran from 2024-07-15 to 2024-07-30."
    )


def test_events_from_decision_recognition_decision_workplace_lowercase():
    """Test events_from_decision with workplace ballot to verify lowercase description"""
    recognition_doc = {
        "decision_date": "2024-08-01",
        "union_recognized": True,
        "form_of_ballot": "Workplace",  # Should become "workplace" in description
        "ballot": {
            "eligible_workers": 100,
            "spoiled_ballots": 2,
            "votes_in_favor": 60,
            "votes_against": 20,
            "start_ballot_period": "2024-07-15",
            "end_ballot_period": "2024-07-30",
        },
        "good_relations_contested": False,
    }

    source_url = "https://example.com/recognition/999"
    decision = Decision[DocumentType.recognition_decision](recognition_doc, source_url)

    events = events_from_decision(decision)

    # Should return 2 events: BallotHeld and UnionRecognized
    assert len(events) == 2

    # Check BallotHeld event has lowercase description
    ballot_event = events[0]
    assert ballot_event.type == EventType.BallotHeld
    assert ballot_event.date == datetime(2024, 7, 15).date()
    assert str(ballot_event.source_document_url) == source_url
    assert (
        ballot_event.description
        == "A workplace ballot with 100 eligible workers ran from 2024-07-15 to 2024-07-30."
    )


def test_events_from_decision_empty_document():
    """Test events_from_decision with empty document"""
    empty_doc = {}

    source_url = "https://example.com/empty/999"
    fallback_date = datetime(2024, 1, 15)
    decision = Decision[DocumentType.application_withdrawn](
        empty_doc, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 1 event using fallback date
    assert len(events) == 1

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[0]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None


def test_events_from_decision_none_document():
    """Test events_from_decision with None document"""
    source_url = "https://example.com/none/999"
    fallback_date = datetime(2024, 1, 15)
    decision = Decision[DocumentType.application_withdrawn](
        None, source_url, fallback_date
    )

    events = events_from_decision(decision)

    # Should return 1 event using fallback date
    assert len(events) == 1

    # Check ApplicationWithdrawn event
    app_withdrawn_event = events[0]
    assert app_withdrawn_event.type == EventType.ApplicationWithdrawn
    assert app_withdrawn_event.date == fallback_date.date()
    assert str(app_withdrawn_event.source_document_url) == source_url
    assert app_withdrawn_event.description is None
