import pytest
from baml_client.async_client import b
from baml_client.types import FormOfBallot
from . import date_eq

@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-united-voices-of-the-world-service-to-the-aged-sage/form-of-ballot-decision"
    ],
)
async def test_uvw_sage(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "16 February 2021")
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Combination
    assert fbd.union_preferred == FormOfBallot.Postal


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5ae8364e40f0b631578af031/Form_of_Ballot_Decision.pdf"
    ],
)
async def test_nuj_buzzfeed(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "30 April 2018")
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Workplace
    assert fbd.union_preferred == FormOfBallot.Postal


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-grissan-carrick-limited-2/form-of-ballot"
    ],
)
async def test_gmb_grissan_carrick(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "7 May 2021")
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Postal
    assert fbd.union_preferred == FormOfBallot.Workplace


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a7ffcdd40f0b62305b887ea/Form_of_Ballot_Decision.pdf"
    ],
)
async def test_rmt_interserve(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "26 March 2015")
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Postal
    assert fbd.union_preferred == FormOfBallot.Workplace


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a86c6f240f0b6230269db2e/Form_of_Ballot_Decision.pdf"
    ],
)
async def test_bfawu_wealmoor(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "14 February 2018")
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Workplace
    assert fbd.union_preferred == FormOfBallot.Postal


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-unite-the-union-moog-controls-limited/form-of-ballot-decision"
    ],
)
async def test_unite_moog(cac_document_contents):
    fbd = await b.ExtractFormOfBallotDecision(cac_document_contents)

    assert date_eq(fbd.decision_date, "7 June 2023")
    assert fbd.form_of_ballot == FormOfBallot.Workplace
    assert fbd.employer_preferred == FormOfBallot.Postal
    assert fbd.union_preferred == FormOfBallot.Workplace
