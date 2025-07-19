import pytest
from baml_client.async_client import b
from baml_client.types import BargainingUnit, RejectionReason
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
    assert ad.petition_signatures == 106
    assert ad.application_date == "8 March 2024"
    assert ad.end_of_acceptance_period == "19 April 2024"
    assert ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="all employees of the British Academy, except Directors and "
        "the Head of HR",
        size=147,
        size_considered=True,
        claimed_membership=50,
        membership=47,
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
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.petition_signatures == 257
    assert ad.application_date == "30 April 2019"
    assert ad.end_of_acceptance_period == "21 June 2019"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Butchery One – Knife Holders, Butchery Two – Knife Holders"
        " and Cutting Lines",
        size=368,
        size_considered=True,
        claimed_membership=100,
        membership=77,
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
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.petition_signatures is None
    assert ad.application_date == "11 August 2022"
    assert ad.end_of_acceptance_period == "14 September 2022"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Motorman, Bosun, Pursers and Able Seaman employed on "
        "board the vessel the Scillonian 111",
        size=12,
        size_considered=True,
        claimed_membership=11,
        membership=10,
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
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.petition_signatures == 21
    assert ad.application_date == "22 September 2014"
    assert ad.end_of_acceptance_period == "24 October 2014"
    assert ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All staff employed to clean Non Advertising Bus Shelters",
        size=42,
        size_considered=True,
        claimed_membership=19,
        membership=17,
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
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.NoMajoritySupportLikely]
    assert ad.petition_signatures == 23
    assert ad.application_date == "2 August 2016"
    assert ad.end_of_acceptance_period == "17 May 2017"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All hourly paid production workers in the paint line "
        "and profiling areas",
        size=27,
        size_considered=True,
        claimed_membership=12,
        membership=9,
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
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.SomeOtherReason]
    assert ad.petition_signatures is None
    assert ad.application_date == "20 November 2017"
    assert not ad.end_of_acceptance_period
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Security Guards, Postroom Workers, AV Staff, Porters, and "
        "Receptionists working for Cordant Security and/at University of London",
        size=69,
        size_considered=True,
        claimed_membership=61,
        membership=None,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/"
        "cac-outcome-pcs-interserve-group-limited/application-progress"
    ],
)
async def test_pcs_interserve_group_limited(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "24 November 2020")
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.SomeOtherReason]
    assert ad.petition_signatures is None
    assert ad.application_date == "3 November 2020"
    assert ad.end_of_acceptance_period == "30 November 2020"
    assert not ad.bargaining_unit_agreed
    assert not ad.bargaining_unit.size_considered


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a7f7775ed915d74e622aa14/Acceptance_Decision.pdf"
    ],
)
async def test_prospect_babcock_offshore(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "21 November 2016")
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.petition_signatures == 47
    assert ad.application_date == "9 September 2016"
    assert ad.end_of_acceptance_period == "21 November 2016"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Those holding either a B1 or B2 licence, or both (as recognised "
        "by the European Aviation Safety Agency and the Civil Aviation Authority) and "
        "employed by Babcock Mission Critical Services Offshore Limited at all of its "
        "operational locations fulfilling the role of licensed aircraft engineers.",
        size=106,
        size_considered=True,
        claimed_membership=47,
        membership=41,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a80619de5274a2e8ab4fd1e/Acceptance_Decision.pdf"
    ],
)
async def test_iwgb_ocean_integrated_services(cac_document_contents):
    ad = await ExtractAcceptanceDecision(cac_document_contents)

    assert date_eq(ad.decision_date, "8 June 2015")
    assert not ad.success
    assert RejectionReason.AnotherUnionAlreadyRecognized in ad.rejection_reasons
    assert ad.application_date == "20 May 2015"
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All employees of Ocean Integrated Services Ltd. at the Royal College of Music site",
        size=0,
        size_considered=False,
        claimed_membership=None,
        membership=None,
    )
