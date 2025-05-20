import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import BallotResult, FormOfBallot
from pipeline.services import anthropic_rate_limit
from tenacity import retry
from . import date_eq


@retry(**anthropic_rate_limit)
async def ExtractRecognitionDecision(content):
    return await b.ExtractRecognitionDecision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-apcoa-parking-uk-ltd/recognition-decision"
    ],
)
async def test_gmb_apcoa_parking(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "2 June 2023")
    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert not rd.ballot
    assert not rd.form_of_ballot


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5b23c36240f0b634b1266d03/Recognition_Decision.pdf"
    ],
)
async def test_unite_mitie_property_services(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "15 June 2018")
    assert rd.union_recognized
    assert rd.good_relations_contested
    assert not rd.ballot
    assert not rd.form_of_ballot


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-sgl-carbon-fibres-limited/recognition-decision"
    ],
)
async def test_gmb_sgl_carbon_fibres(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "24 May 2022")
    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.form_of_ballot == FormOfBallot.Postal
    assert rd.ballot == BallotResult(
        eligible_workers=38,
        spoiled_ballots=0,
        votes_in_favor=16,
        votes_against=8,
        start_ballot_period="27 April 2022",
        end_ballot_period="11 May 2022",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcomeunite-the-union-international-baccalaureate-orguk/recognition-decision"
    ],
)
async def test_unite_international_baccalaureate(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "17 July 2019")
    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.form_of_ballot == FormOfBallot.Combination
    assert rd.ballot == BallotResult(
        eligible_workers=242,
        spoiled_ballots=1,
        votes_in_favor=156,
        votes_against=13,
        start_ballot_period="3 July 2019",
        end_ballot_period="15 July 2019",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-nasuwt-neu-radley-college-2/recognition-decision"
    ],
)
async def test_nasuwt_radley_college(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "23 October 2023")
    assert not rd.union_recognized
    assert rd.good_relations_contested
    assert rd.form_of_ballot == FormOfBallot.Postal
    assert rd.ballot == BallotResult(
        eligible_workers=114,
        spoiled_ballots=1,
        votes_in_favor=33,
        votes_against=60,
        start_ballot_period="26 September 2023",
        end_ballot_period="9 October 2023",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-pda-boots-management-services-ltd-2/recognition-decision"
    ],
)
async def test_pda_boots_management_services(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "13 March 2019")
    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.form_of_ballot == FormOfBallot.Postal
    assert rd.ballot == BallotResult(
        eligible_workers=6803,
        spoiled_ballots=0,
        votes_in_favor=3229,
        votes_against=266,
        start_ballot_period="18 February 2019",
        end_ballot_period="11 March 2019",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a7f768140f0b62305b874bf/Recognition_Decision.pdf"
    ],
)
async def test_unite_sgs_united_kingdom(cac_document_contents):
    rd = await ExtractRecognitionDecision(cac_document_contents)

    assert date_eq(rd.decision_date, "11 November 2015")
    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.form_of_ballot == FormOfBallot.Postal
    assert rd.ballot == BallotResult(
        eligible_workers=52,
        spoiled_ballots=0,
        votes_in_favor=29,
        votes_against=0,
        start_ballot_period="23 October 2015",
        end_ballot_period="5 November 2015",
    )
