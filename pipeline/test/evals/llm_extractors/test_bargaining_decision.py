import pytest
from baml_client.async_client import b
from . import date_eq


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-london-ashford-airport-ltd-2/method-decision"
    ],
)
async def test_prospect_ashford_airport(cac_document_contents):
    bd = await b.ExtractBargainingDecision(cac_document_contents)

    assert date_eq(bd.decision_date, "11 January 2024")
    assert date_eq(bd.cac_involvement_date, "8 December 2023")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-unite-the-union-hayakawa-international-uk-limited-2/method-decision"
    ],
)
async def test_unite_hayakawa_international(cac_document_contents):
    bd = await b.ExtractBargainingDecision(cac_document_contents)

    assert date_eq(bd.decision_date, "26 October 2020")
    assert date_eq(bd.cac_involvement_date, "7 October 2020")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-rmt-bespoke-facilities-management/method-decision"
    ],
)
async def test_rmt_bespoke_facilities_management(cac_document_contents):
    bd = await b.ExtractBargainingDecision(cac_document_contents)

    assert date_eq(bd.decision_date, "11 July 2023")
    assert date_eq(bd.cac_involvement_date, "25 May 2023")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-pcs-axis-security-services-ltd/method-decision"
    ],
)
async def test_pcs_axis_security_services(cac_document_contents):
    bd = await b.ExtractBargainingDecision(cac_document_contents)

    assert date_eq(bd.decision_date, "16 April 2021")
    assert date_eq(bd.cac_involvement_date, "24 February 2021")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-ucu-university-of-brighton/method-decision"
    ],
)
async def test_ucu_university_of_brighton(cac_document_contents):
    bd = await b.ExtractBargainingDecision(cac_document_contents)

    assert date_eq(bd.decision_date, "30 January 2023")
    assert date_eq(bd.cac_involvement_date, "7 October 2022")
