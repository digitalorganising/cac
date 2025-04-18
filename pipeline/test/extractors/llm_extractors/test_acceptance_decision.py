import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import BargainingUnit, RejectionReason
from pipeline.services import anthropic_rate_limit
from tenacity import retry
from . import date_eq


@retry(**anthropic_rate_limit)
async def ExtractAcceptanceDecision(content):
    return await b.ExtractAcceptanceDecision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-tur113942024-prospect-the-british-academy-for-the-promotion-of-historical-philosophical-and-philological-studies-the-bri/application-progress"
    ],
)
async def test_prospect_british_academy(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "17 April 2024")
    assert ad.success
    assert not ad.rejection_reasons
    assert 0 <= ad.employer_hostility <= 100
    assert ad.application_date == "8 March 2024"
    assert ad.end_of_acceptance_period == "19 April 2024"
    assert ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="all employees of the British Academy, except Directors and "
        "the Head of HR",
        size=147,
        claimed_membership=50,
        membership=47,
        supporters=95,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/"
        "cac-outcome-gmb-cranswick-country-foods/acceptance-decision"
    ],
)
async def test_gmb_cranswick_country_foods(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "19 June 2019")
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "30 April 2019"
    assert ad.end_of_acceptance_period == "21 June 2019"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Butchery One – Knife Holders, Butchery Two – Knife Holders"
        " and Cutting Lines",
        size=368,
        claimed_membership=100,
        membership=77,
        supporters=147,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/"
        "cac-outcome-rmt-isle-of-scilly-steamship-company-ltd/application-progress"
    ],
)
async def test_rmt_isles_of_scilly_shipping(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "8 September 2022")
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "11 August 2022"
    assert ad.end_of_acceptance_period == "14 September 2022"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Motorman, Bosun, Pursers and Able Seaman employed on "
        "board the vessel the Scillonian 111",
        size=12,
        claimed_membership=11,
        membership=10,
        supporters=10,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a7df4fd40f0b623026883a3/Acceptance_Decision.pdf"
    ],
)
async def test_gmb_mitie_services(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "23 October 2014")
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "22 September 2014"
    assert ad.end_of_acceptance_period == "24 October 2014"
    assert ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All staff employed to clean Non Advertising Bus Shelters",
        size=42,
        claimed_membership=19,
        membership=17,
        supporters=20,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a81e58840f0b62305b91651/Acceptance_Decision.pdf"
    ],
)
async def test_community_coilcolor(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "17 May 2017")
    assert 0 <= ad.employer_hostility <= 100
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.NoMajoritySupportLikely]
    assert ad.application_date == "2 August 2016"
    assert ad.end_of_acceptance_period == "17 May 2017"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All hourly paid production workers in the paint line "
        "and profiling areas",
        size=27,
        claimed_membership=12,
        membership=9,
        supporters=None,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a820a5ae5274a2e87dc0d5b/Acceptance_Decision.pdf"
    ],
)
async def test_iwgb_university_of_london(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "10 January 2018")
    assert 0 <= ad.employer_hostility <= 100
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.SomeOtherReason]
    assert ad.application_date == "20 November 2017"
    assert not ad.end_of_acceptance_period
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Security Guards, Postroom Workers, AV Staff, Porters, and "
        "Receptionists working for Cordant Security and/at University of London",
        size=69,
        claimed_membership=61,
        membership=None,
        supporters=None,
    )
