import pytest
from pipeline.types.outcome import Outcome
from pydantic import ValidationError


def test_outcome_model_validation():
    valid_outcome = {
        "id": "TUR1/1234(2025):application_withdrawn",
        "last_updated": "2025-01-01",
        "outcome_url": "http://test.outcome/1234",
        "outcome_title": "Test union & test employer",
        "documents": {},
        "document_urls": {},
        "extracted_data": {},
    }
    invalid_outcome = {
        **valid_outcome,
        "last_updated": None,
    }

    Outcome.model_validate(valid_outcome)
    with pytest.raises(ValidationError):
        Outcome.model_validate(invalid_outcome)
