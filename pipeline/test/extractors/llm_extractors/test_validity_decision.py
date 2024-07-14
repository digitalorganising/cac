from difflib import SequenceMatcher as SM

import pytest
from pipeline.baml_client import b
from pipeline.baml_client.types import BargainingUnit, RejectionReason


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a7dee2d40f0b62305b7faf9/Validity_Decision.pdf"
    ],
)
async def test_unite_primopost(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert vd.decision_date == "2014-06-25"
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
    assert vd.new_bargaining_unit.claimed_membership == 35
    assert vd.new_bargaining_unit.membership == 35
    assert vd.new_bargaining_unit.supporters == 51


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-rmt-cwind-2/validity-decision"
    ],
)
async def test_rmt_cwind(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert vd.decision_date == "2019-11-14"
    assert not vd.valid
    assert vd.new_bargaining_unit == BargainingUnit(
        description="all Skippers and Crew employed by CWind except those based at "
        "the Ramsgate site "
        "that were subject to the existing bargaining arrangements",
        size=16,
        claimed_membership=7,
        membership=5,
        supporters=0,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-the-noble-collection-uk-limited/validity-decision"
    ],
)
async def test_gmb_noble_collection(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert vd.decision_date == "2022-11-02"
    assert vd.valid
    assert not vd.rejection_reasons
    assert vd.new_bargaining_unit == BargainingUnit(
        description="all retail staff employed by the Noble Collection UK "
        "Ltd at 26-28 Neal Street, "
        "London WC2 and Hamleys Toy Store, "
        "188-196 Regent Street, London W1 excluding the Head of the Retail Team",
        size=15,
        claimed_membership=7,
        membership=7,
        supporters=7,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-bectu-the-corporation-of-the-hall-of-arts-and-sciences/validity-decision"
    ],
)
async def test_bectu_hall_of_arts_and_sciences(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert vd.decision_date == "2019-03-04"
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
        claimed_membership=58,
        membership=58,
        supporters=199,
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a8068ffe5274a2e87db9a6f/Validity_Decision.pdf"
    ],
)
async def test_gmb_metallink(cac_document_contents):
    vd = await b.ExtractValidityDecision(cac_document_contents)

    assert vd.decision_date == "2016-04-05"
    assert not vd.valid
    assert vd.rejection_reasons == [RejectionReason.NoMajoritySupportLikely]
    assert vd.new_bargaining_unit == BargainingUnit(
        description="All employees excluding management",
        size=38,
        claimed_membership=11,
        membership=11,
        supporters=14,
    )
