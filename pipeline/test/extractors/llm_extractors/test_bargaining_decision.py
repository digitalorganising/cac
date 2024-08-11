import pytest
from pipeline.baml_client.async_client import b
from pipeline.services import anthropic_rate_limit
from tenacity import retry


@retry(**anthropic_rate_limit)
async def ExtractBargainingDecision(content):
    return await b.ExtractBargainingDecision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-london-ashford-airport-ltd-2/method-decision"
    ],
)
async def test_prospect_ashford_airport(cac_document_contents):
    bd = await ExtractBargainingDecision(cac_document_contents)

    assert bd.decision_date == "2024-01-11"
    assert bd.cac_involvement_date == "2023-12-08"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-unite-the-union-hayakawa-international-uk-limited-2/method-decision"
    ],
)
async def test_unite_hayakawa_international(cac_document_contents):
    bd = await ExtractBargainingDecision(cac_document_contents)

    assert bd.decision_date == "2020-10-26"
    assert bd.cac_involvement_date == "2020-10-07"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-rmt-bespoke-facilities-management/method-decision"
    ],
)
async def test_rmt_bespoke_facilities_management(cac_document_contents):
    bd = await ExtractBargainingDecision(cac_document_contents)

    assert bd.decision_date == "2023-07-11"
    assert bd.cac_involvement_date == "2023-05-25"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-pcs-axis-security-services-ltd/method-decision"
    ],
)
async def test_pcs_axis_security_services(cac_document_contents):
    bd = await ExtractBargainingDecision(cac_document_contents)

    assert bd.decision_date == "2021-04-16"
    assert bd.cac_involvement_date == "2021-02-24"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-ucu-university-of-brighton/method-decision"
    ],
)
async def test_ucu_university_of_brighton(cac_document_contents):
    bd = await ExtractBargainingDecision(cac_document_contents)

    assert bd.decision_date == "2023-01-30"
    assert bd.cac_involvement_date == "2022-10-07"
