import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import BargainingUnit, Panel, RejectionReason


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-tur113942024-prospect-the-british-academy-for-the-promotion-of-historical-philosophical-and-philological-studies-the-bri/application-progress"
    ],
)
async def test_prospect_british_academy(cac_document_contents):
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2024-04-17"
    assert ad.union_name == "Prospect"
    assert (
        ad.employer_name == "The British Academy for the Promotion of Historical "
        "Philosophical and Philological Studies"
    )
    assert ad.success
    assert not ad.rejection_reasons
    assert 0 <= ad.employer_hostility <= 100
    assert ad.application_date == "2024-03-08"
    assert ad.end_of_acceptance_period == "2024-04-19"
    assert ad.panel == Panel(
        case_manager="Joanne Curtis",
        panel_members=sorted(["Laura Prince", "Richard Fulham", "Nicholas Childs"]),
    )
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
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2019-06-19"
    assert ad.union_name == "GMB"
    assert ad.employer_name == "Cranswick Country Foods"
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "2019-04-30"
    assert ad.end_of_acceptance_period == "2019-06-21"
    assert ad.panel == Panel(
        case_manager="Linda Lehan",
        panel_members=sorted(["James Tayler", "Tom Keeney", "David Coats"]),
    )
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
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2022-09-08"
    assert ad.union_name == "RMT"
    assert ad.employer_name == "Isles of Scilly Shipping (Guernsey) Ltd"
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "2022-08-11"
    assert ad.end_of_acceptance_period == "2022-09-14"
    assert ad.panel == Panel(
        case_manager="Joanne Curtis",
        panel_members=sorted(["Sarah Havlin", "Susan Jordan", "Joanna Brown"]),
    )
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
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2014-10-23"
    assert ad.union_name == "GMB"
    assert ad.employer_name == "Mitie Services Ltd"
    assert 0 <= ad.employer_hostility <= 100
    assert ad.success
    assert not ad.rejection_reasons
    assert ad.application_date == "2014-09-22"
    assert ad.end_of_acceptance_period == "2014-10-24"
    assert ad.panel == Panel(
        case_manager="Linda Lehan",
        panel_members=sorted(["Lynette Harris", "Len Aspell", "Bob Purkiss"]),
    )
    assert ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All staff employed to clean Non Advertising Bus Shelters",
        size=42,
        claimed_membership=19,
        membership=17,
        supporters=22,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a81e58840f0b62305b91651/Acceptance_Decision.pdf"
    ],
)
async def test_community_coilcolor(cac_document_contents):
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2017-05-17"
    assert ad.union_name == "Community Union"
    assert ad.employer_name == "Coilcolor Limited"
    assert 0 <= ad.employer_hostility <= 100
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.NoMajoritySupportLikely]
    assert ad.application_date == "2016-08-02"
    assert ad.end_of_acceptance_period == "2017-05-17"
    assert ad.panel == Panel(
        case_manager="Sharmin Khan",
        panel_members=sorted(["Gillian Morris", "Michael Shepherd", "Lesley Mercer"]),
    )
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="All hourly paid production workers in the paint line "
        "and profiling areas",
        size=27,
        claimed_membership=12,
        membership=9,
        supporters=16,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/"
        "5a820a5ae5274a2e87dc0d5b/Acceptance_Decision.pdf"
    ],
)
async def test_iwgb_university_of_london(cac_document_contents):
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.decision_date == "2018-01-10"
    assert ad.union_name == "Independent Workers' Union of Great Britain (IWGB)"
    assert ad.employer_name == "University of London"
    assert 0 <= ad.employer_hostility <= 100
    assert not ad.success
    assert ad.rejection_reasons == [RejectionReason.SomeOtherReason]
    assert ad.application_date == "2017-11-20"
    assert ad.end_of_acceptance_period == "2017-12-11"
    assert ad.panel == Panel(
        case_manager="Nigel Cookson",
        panel_members=sorted(["Barry Clarke", "David Coats", "Roger Roberts"]),
    )
    assert not ad.bargaining_unit_agreed
    assert ad.bargaining_unit == BargainingUnit(
        description="Security Guards, Postroom Workers, AV Staff, Porters, and "
        "Receptionists working for Cordant Security and/at University of London",
        size=69,
        claimed_membership=61,
        membership=61,
        supporters=35,
    )
