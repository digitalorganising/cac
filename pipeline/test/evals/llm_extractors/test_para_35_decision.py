import pytest
from baml_client.async_client import b
from baml_client.types import Para35Decision
from pipeline.services import anthropic_rate_limit
from tenacity import retry
from . import date_eq


@retry(**anthropic_rate_limit)
async def ExtractPara35Decision(content):
    return await b.ExtractPara35Decision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-wincanton/application-progress"
    ],
)
async def test_gmb_wincanton(cac_document_contents):
    p35d = await ExtractPara35Decision(cac_document_contents)

    assert date_eq(p35d.decision_date, "07 November 2023")
    assert not p35d.application_can_proceed
    assert p35d.application_date == "22 September 2023"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-rmt-carlisle-security-services/paragraph-35-decision"
    ],
)
async def test_rmt_carlisle_security_services(cac_document_contents):
    p35d = await ExtractPara35Decision(cac_document_contents)

    assert date_eq(p35d.decision_date, "07 May 2020")
    assert p35d.application_can_proceed
    assert p35d.application_date == "14 February 2020"
