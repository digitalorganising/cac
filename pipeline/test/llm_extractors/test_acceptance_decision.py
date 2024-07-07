import pytest
from pipeline.baml_client import b
from pipeline.baml_client.types import BargainingUnit, Panel, Petition


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-prospect-tur113942024-prospect-the-british-academy-for-the-promotion-of-historical-philosophical-and-philological-studies-the-bri/application-progress"
    ],
)
async def test_prospect_british_academy(cac_document_contents):
    ad = await b.ExtractAcceptanceDecision(cac_document_contents)
    ad.panel.panel_members.sort()

    assert ad.union_name == "Prospect"
    assert (
        ad.employer_name == "The British Academy for the Promotion of Historical "
        "Philosophical and Philological Studies"
    )
    assert ad.success
    assert ad.application_date == "2024-03-08"
    assert ad.end_of_acceptance_period == "2024-04-19"
    assert ad.panel == Panel(
        case_manager="Joanne Curtis",
        panel_members=sorted(
            ["Ms Laura Prince K.C.", "Mr Richard Fulham", "Mr Nicholas Childs"]
        ),
    )
    assert ad.bargaining_unit == BargainingUnit(
        description="all employees of the British Academy, except Directors and "
        "the Head of HR",
        agreed=True,
        size=147,
        claimed_membership=50,
        membership=47,
    )
    assert (
        Petition(
            source="union",
            in_favor=106,
            in_bargaining_unit=95,
            members=40,
            non_members=55,
        )
        in ad.petitions
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

    assert ad.union_name == "GMB"
    assert ad.employer_name == "Cranswick Country Foods"
    assert ad.success
    assert ad.application_date == "2019-04-30"
    assert ad.end_of_acceptance_period == "2019-06-21"
    assert ad.panel == Panel(
        case_manager="Linda Lehan",
        panel_members=sorted(["Mr James Tayler", "Mr Tom Keeney", "Mr David Coats"]),
    )
    assert ad.bargaining_unit == BargainingUnit(
        description="Butchery One – Knife Holders, Butchery Two – Knife Holders"
        " and Cutting Lines",
        agreed=False,
        size=368,
        claimed_membership=100,
        membership=77,
    )
    assert (
        Petition(
            source="union",
            in_favor=257,
            in_bargaining_unit=147,
            members=43,
            non_members=104,
        )
        in ad.petitions
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

    assert ad.union_name == "RMT"
    assert ad.employer_name == "Isles of Scilly Shipping (Guernsey) Ltd"
    assert ad.success
    assert ad.application_date == "2022-08-11"
    assert ad.end_of_acceptance_period == "2022-09-14"
    assert ad.panel == Panel(
        case_manager="Joanne Curtis",
        panel_members=sorted(
            ["Mrs Sarah Havlin", "Mrs Susan Jordan", "Ms Joanna Brown"]
        ),
    )
    assert ad.bargaining_unit == BargainingUnit(
        description="Motorman, Bosun, Pursers and Able Seaman employed on "
        "board the vessel the Scillonian 111",
        agreed=False,
        size=12,
        claimed_membership=11,
        membership=10,
    )
    assert ad.petitions == []


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

    assert ad.union_name == "GMB"
    assert ad.employer_name == "Mitie Services Ltd"
    assert ad.success
    assert ad.application_date == "2014-09-22"
    assert ad.end_of_acceptance_period == "2014-10-24"
    assert ad.panel == Panel(
        case_manager="Linda Lehan",
        panel_members=sorted(
            ["Professor Lynette Harris", "Mr. Len Aspell", "Mr. Bob Purkiss MBE"]
        ),
    )
    assert ad.bargaining_unit == BargainingUnit(
        description="All staff employed to clean Non Advertising Bus Shelters",
        agreed=True,
        size=42,
        claimed_membership=19,
        membership=17,
    )
    assert (
        Petition(
            source="union",
            in_favor=21,
            in_bargaining_unit=20,
            members=15,
            non_members=5,
        )
        in ad.petitions
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

    assert ad.union_name == "Community Union"
    assert ad.employer_name == "Coilcolor Limited"
    assert not ad.success
    assert ad.application_date == "2016-08-02"
    assert ad.end_of_acceptance_period == "2017-05-17"
    assert ad.panel == Panel(
        case_manager="Miss Sharmin Khan",
        panel_members=sorted(
            ["Professor Gillian Morris", "Mr Michael Shepherd", "Ms Lesley Mercer"]
        ),
    )
    assert ad.bargaining_unit == BargainingUnit(
        description="All hourly paid production workers in the paint line "
        "and profiling areas",
        agreed=False,
        size=27,
        claimed_membership=12,
        membership=9,
    )
    assert (
        Petition(
            source="union",
            in_favor=23,
            in_bargaining_unit=20,
            members=9,
            non_members=11,
        )
        in ad.petitions
    )
    assert (
        Petition(
            source="employer",
            in_favor=7,
            in_bargaining_unit=16,
            members=2,
            non_members=14,
        )
        in ad.petitions
    )
