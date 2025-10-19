from difflib import SequenceMatcher as SM

import pytest
from baml_client.async_client import b
from baml_client.types import BargainingUnit, RejectionReason
from . import date_eq


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a7dee2d40f0b62305b7faf9/Validity_Decision.pdf"
    ],
)
async def test_unite_primopost(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert date_eq(vd.decision_date, "25 June 2014")
    assert vd.valid
    assert (
        SM(
            None,
            """All direct and indirect operations based employees at Primopost, Buxton 
            in either
permanent, temporary, trainee or apprentice employment, with the following job titles:
No.1 Printer
No.2 Printer (Assistant Printer)
PMR Operative or Assistant
Ink Technician
Factory Operative - Lamination/Coldseal, Slitting, Core Cutting or Warehouse, Finishing
Administrator
Maintenance Engineer
Factory Cleaner
But not including Shift or Team Leaders, Office based employees or Company
Management""",
            vd.new_bargaining_unit.description,
        ).ratio()
        > 0.90
    )

    assert vd.new_bargaining_unit.size == 69
    assert vd.new_bargaining_unit.claimed_membership is 35
    assert vd.new_bargaining_unit.membership == 35


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-rmt-cwind-2/validity-decision"
    ],
)
async def test_rmt_cwind(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert date_eq(vd.decision_date, "14 November 2019")
    assert not vd.valid
    assert vd.new_bargaining_unit == BargainingUnit(
        description="all Skippers and Crew employed by CWind except those based at the Ramsgate site "
        "that were subject to the existing bargaining arrangements",
        size=16,
        size_considered=True,
        claimed_membership=7,
        membership=5,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-the-noble-collection-uk-limited/validity-decision"
    ],
)
async def test_gmb_noble_collection(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert date_eq(vd.decision_date, "2 November 2022")
    assert vd.valid
    assert not vd.rejection_reasons
    assert (
        SM(
            None,
            "all retail staff employed by the Noble Collection UK "
            "Ltd at 26-28 Neal Street, "
            "London WC2 and Hamleys Toy Store, "
            "188-196 Regent Street, London W1 excluding the Head of the Retail Team",
            vd.new_bargaining_unit.description,
        ).ratio()
        > 0.90
    )
    assert vd.new_bargaining_unit.size == 15
    assert vd.new_bargaining_unit.claimed_membership == 7
    assert vd.new_bargaining_unit.membership == 7
    assert vd.new_bargaining_unit.size_considered


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-bectu-the-corporation-of-the-hall-of-arts-and-sciences/validity-decision"
    ],
)
async def test_bectu_hall_of_arts_and_sciences(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert date_eq(vd.decision_date, "4 March 2019")
    assert vd.valid
    assert not vd.rejection_reasons
    assert vd.new_bargaining_unit == BargainingUnit(
        description="All staff employed by the Corporation of the Hall of Arts and "
        "Sciences (commonly known as the Royal Albert Hall) at the "
        "Royal Albert Hall below Heads of Department and senior executive "
        "grades in the following areas: Box Office, Facilities and "
        "Building Services, Front of House, Security, Tours and "
        "Production and Technical",
        size=448,
        size_considered=True,
        claimed_membership=58,
        membership=58,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a8068ffe5274a2e87db9a6f/Validity_Decision.pdf"
    ],
)
async def test_gmb_metallink(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert date_eq(vd.decision_date, "5 April 2016")
    assert not vd.valid
    assert vd.rejection_reasons == [RejectionReason.NoMajoritySupportLikely]
    assert vd.new_bargaining_unit == BargainingUnit(
        description="All employees excluding management",
        size=38,
        size_considered=True,
        claimed_membership=11,
        membership=11,
    )
