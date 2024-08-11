import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import FormOfBallot
from pipeline.services import anthropic_rate_limit
from tenacity import retry


@retry(**anthropic_rate_limit)
async def ExtractFormOfBallotDecision(content):
    return await b.ExtractFormOfBallotDecision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-united-voices-of-the-world-service-to-the-aged-sage/form-of-ballot-decision"
    ],
)
async def test_uvw_sage(cac_document_contents):
    fbd = await ExtractFormOfBallotDecision(cac_document_contents)

    assert fbd.decision_date == "2021-02-16"
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
    fbd = await ExtractFormOfBallotDecision(cac_document_contents)

    assert fbd.decision_date == "2018-04-30"
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
    fbd = await ExtractFormOfBallotDecision(cac_document_contents)

    assert fbd.decision_date == "2021-05-07"
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
    fbd = await ExtractFormOfBallotDecision(cac_document_contents)

    assert fbd.decision_date == "2015-03-26"
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
    fbd = await ExtractFormOfBallotDecision(cac_document_contents)

    assert fbd.decision_date == "2018-02-14"
    assert fbd.form_of_ballot == FormOfBallot.Postal
    assert fbd.employer_preferred == FormOfBallot.Workplace
    assert fbd.union_preferred == FormOfBallot.Postal
