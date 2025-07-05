import pytest
from baml_client.async_client import b
from baml_client.types import Party
from pipeline.services import anthropic_rate_limit
from tenacity import retry
from . import date_eq


@retry(**anthropic_rate_limit)
async def ExtractAccessDecisionOrDispute(content):
    return await b.ExtractAccessDecisionOrDispute(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-dyer-engineering-ltd/paragraph-26-decision"
    ],
)
async def test_gmb_dyer_engineering(cac_document_contents):
    ad = await ExtractAccessDecisionOrDispute(cac_document_contents)

    assert date_eq(ad.decision_date, "5 February 2021")
    assert ad.details.complainant == Party.Union
    assert ad.details.upheld


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-prestwick-aircraft-maintenance-limited/access-arrangements-for-ballot-decision"
    ],
)
async def test_prospect_prestwick_aircraft_maintenance(cac_document_contents):
    ad = await ExtractAccessDecisionOrDispute(cac_document_contents)

    assert date_eq(ad.decision_date, "22 November 2021")
    assert not ad.details.favors
    assert "virtual" in ad.details.description.lower()


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a81c0c5e5274a2e87dbf4af/Access_Decision.pdf"
    ],
)
async def test_rmt_carefree_travel(cac_document_contents):
    ad = await ExtractAccessDecisionOrDispute(cac_document_contents)

    assert date_eq(ad.decision_date, "06 June 2017")
    assert ad.details.favors == Party.Union
    assert "canteen" in ad.details.description.lower()


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-united-voices-of-the-world-ocs-group-uk-limited/paragraph-26-decision"
    ],
)
async def test_uvw_ocs_group(cac_document_contents):
    ad = await ExtractAccessDecisionOrDispute(cac_document_contents)

    assert date_eq(ad.decision_date, "12 June 2020")
    assert ad.details.complainant == Party.Union
    assert not ad.details.upheld


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-urtu-eddie-stobart-limited/access-decision"
    ],
)
async def test_urtu_eddie_stobart(cac_document_contents):
    ad = await ExtractAccessDecisionOrDispute(cac_document_contents)

    assert date_eq(ad.decision_date, "12 October 2021")
    assert ad.details.favors == Party.Employer
    assert "virtual" in ad.details.description.lower()
