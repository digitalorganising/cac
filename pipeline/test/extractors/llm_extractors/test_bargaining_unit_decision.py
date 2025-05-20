from difflib import SequenceMatcher as SM

import pytest
from pipeline.baml_client.async_client import b
from pipeline.services import anthropic_rate_limit
from tenacity import retry
from . import date_eq


@retry(**anthropic_rate_limit)
async def ExtractBargainingUnitDecision(content):
    return await b.ExtractBargainingUnitDecision(content)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-nuj-the-press-association-ltd/bargaining-unit-decision"
    ],
)
async def test_nuj_press_association(cac_document_contents):
    bud = await ExtractBargainingUnitDecision(cac_document_contents)

    assert date_eq(bud.decision_date, "17 April 2024")
    assert bud.appropriate_unit_differs
    assert bud.lawyer_present
    assert (
        SM(
            None,
            bud.new_bargaining_unit_description,
            "editorial roles which ultimately report "
            "to the Editor in Chief, barring the senior management roles and the following "
            "positions (the Deputies positions): "
            "Deputy Chief News Editor, Deputy Real Life and "
            "Social Media Editor, "
            "Lifestyle Editor, Puzzles Deputy, Deputy Editor Entertainment, Deputy "
            "Sports Editor, Scotland "
            "Deputy Editor, Group Picture Editor, Deputy Head of Video, Deputy "
            "Business Editor, Deputy Head "
            "of Production, Head of Features, Deputy Picture Editor, Page Production Editor",
        ).ratio()
        > 0.9
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-gmb-eddie-stobart/bargaining-unit-decision"
    ],
)
async def test_gmb_eddie_stobart(cac_document_contents):
    bud = await ExtractBargainingUnitDecision(cac_document_contents)

    assert date_eq(bud.decision_date, "29 October 2021")
    assert bud.appropriate_unit_differs
    assert bud.lawyer_present
    assert (
        SM(
            None,
            bud.new_bargaining_unit_description,
            "Employees employed by Eddie Stobart Limited in its warehouse at "
            "Braunston, Leicester LE3 1ED, "
            "who were: (i) Warehouse Operatives; (ii) Warehouse Packing "
            "Sorters; (iii) Warehouse Loaders; "
            "and (iv) Warehouse Hygienists",
        ).ratio()
        > 0.95
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5a81b71ae5274a2e87dbf1f4/Bargaining_Unit_Decision.pdf"
    ],
)
async def test_rmt_city_cruises(cac_document_contents):
    bud = await ExtractBargainingUnitDecision(cac_document_contents)

    assert date_eq(bud.decision_date, "20 July 2015")
    assert not bud.appropriate_unit_differs
    assert bud.lawyer_present
    assert not bud.new_bargaining_unit_description


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-pcs-union-mitie-group-plc/bargaining-unit-decision"
    ],
)
async def test_pcs_mitie_group(cac_document_contents):
    bud = await ExtractBargainingUnitDecision(cac_document_contents)

    assert date_eq(bud.decision_date, "14 February 2023")
    assert bud.appropriate_unit_differs
    assert bud.lawyer_present
    assert (
        SM(
            None,
            bud.new_bargaining_unit_description,
            "Security personnel, facilities management staff (cleaning and "
            "maintenance), catering/kitchen staff and mail room staff working "
            "for Mitie at Abercrombie House, Foreign Commonwealth and Development "
            "Office "
            "(FCDO) Eaglesham Road, East Kilbride, G75 8EA. For the purposes of this "
            "definition ‘staff’ covers the "
            "following job roles (or similar titles in these areas of work): "
            "Cleaners/housekeeping/cleaning team leader "
            "Security guards/operatives Security supervisors/ "
            "line managers Maintenance workers Mail/post room "
            "operative/staff Catering/Kitchen general assistants Catering/Kitchen "
            "chefs/supervisors "
            "All ‘first line’ management roles, namely; Chef Manager (also referred "
            "to as Catering Manager), Cleaning "
            "Manager, Security Duty Manager, and Site Security Manager (also referred "
            "to as Abercrombie Site Manager, "
            "but excluding the Workplace Manager (also referred to as Facilities "
            "Manager).",
        ).ratio()
        > 0.95
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-unison-addaction/bargaining-unit-decision"
    ],
)
async def test_unison_addaction(cac_document_contents):
    bud = await ExtractBargainingUnitDecision(cac_document_contents)

    assert date_eq(bud.decision_date, "21 August 2020")
    assert not bud.appropriate_unit_differs
    assert not bud.lawyer_present
    assert not bud.new_bargaining_unit_description
