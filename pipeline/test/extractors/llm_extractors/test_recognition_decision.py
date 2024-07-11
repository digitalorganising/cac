import pytest
from pipeline.baml_client import b
from pipeline.baml_client.types import BallotResult


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-apcoa-parking-uk-ltd/recognition-decision"
    ],
)
async def test_gmb_apcoa_parking(cac_document_contents):
    rd = await b.ExtractRecognitionDecision(cac_document_contents)

    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert not rd.ballot


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5b23c36240f0b634b1266d03/Recognition_Decision.pdf"
    ],
)
async def test_unite_mitie_property_services(cac_document_contents):
    rd = await b.ExtractRecognitionDecision(cac_document_contents)

    assert rd.union_recognized
    assert rd.good_relations_contested
    assert not rd.ballot


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-sgl-carbon-fibres-limited/recognition-decision"
    ],
)
async def test_gmb_sgl_carbon_fibres(cac_document_contents):
    rd = await b.ExtractRecognitionDecision(cac_document_contents)

    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.ballot == BallotResult(
        eligible_workers=38,
        spoiled_ballots=0,
        votes_in_favor=16,
        votes_against=8,
        start_ballot_period="2022-04-27",
        end_ballot_period="2022-05-11",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcomeunite-the-union-international-baccalaureate-orguk/recognition-decision"
    ],
)
async def test_unite_international_baccalaureate(cac_document_contents):
    rd = await b.ExtractRecognitionDecision(cac_document_contents)

    assert rd.union_recognized
    assert not rd.good_relations_contested
    assert rd.ballot == BallotResult(
        eligible_workers=242,
        spoiled_ballots=1,
        votes_in_favor=156,
        votes_against=13,
        start_ballot_period="2019-07-03",
        end_ballot_period="2019-07-15",
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-nasuwt-neu-radley-college-2/recognition-decision"
    ],
)
async def test_nasuwt_radley_college(cac_document_contents):
    rd = await b.ExtractRecognitionDecision(cac_document_contents)

    assert not rd.union_recognized
    assert rd.good_relations_contested
    assert rd.ballot == BallotResult(
        eligible_workers=114,
        spoiled_ballots=1,
        votes_in_favor=33,
        votes_against=60,
        start_ballot_period="2023-09-26",
        end_ballot_period="2023-10-09",
    )
