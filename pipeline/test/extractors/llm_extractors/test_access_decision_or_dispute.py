import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import Party


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-dyer-engineering-ltd/paragraph-26-decision"
    ],
)
async def test_gmb_dyer_engineering(cac_document_contents):
    ad = await b.ExtractAccessDecisionOrDispute(cac_document_contents)

    assert ad.decision_date == "2021-02-05"
    assert ad.details.complainant == Party.Union
    assert ad.details.upheld


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-prestwick-aircraft-maintenance-limited/access-arrangements-for-ballot-decision"
    ],
)
async def test_prospect_prestwick_aircraft_maintenance(cac_document_contents):
    ad = await b.ExtractAccessDecisionOrDispute(cac_document_contents)

    assert ad.decision_date == "2021-11-22"
    assert not ad.details.favors
    assert "virtual means" in ad.details.description


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a81c0c5e5274a2e87dbf4af/Access_Decision.pdf"
    ],
)
async def test_rmt_carefree_travel(cac_document_contents):
    ad = await b.ExtractAccessDecisionOrDispute(cac_document_contents)

    assert ad.decision_date == "2017-06-06"
    assert ad.details.complainant == Party.Union
    assert ad.details.upheld


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-united-voices-of-the-world-ocs-group-uk-limited/paragraph-26-decision"
    ],
)
async def test_uvw_ocs_group(cac_document_contents):
    ad = await b.ExtractAccessDecisionOrDispute(cac_document_contents)

    assert ad.decision_date == "2020-06-12"
    assert ad.details.complainant == Party.Union
    assert not ad.details.upheld


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-urtu-eddie-stobart-limited/access-decision"
    ],
)
async def test_urtu_eddie_stobart(cac_document_contents):
    ad = await b.ExtractAccessDecisionOrDispute(cac_document_contents)

    assert ad.decision_date == "2021-10-12"
    assert ad.details.favors == Party.Employer
    assert "virtual means" in ad.details.description
