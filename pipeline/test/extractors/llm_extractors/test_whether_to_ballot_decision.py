import pytest
from pipeline.baml_client.async_client import b
from pipeline.baml_client.types import QualifyingCondition


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-nasuwt-neu-radley-college-2/whether-to-ballot-decision"
    ],
)
async def test_neu_radley_college(cac_document_contents):
    wtbd = await b.ExtractWhetherToBallotDecision(cac_document_contents)

    assert wtbd.decision_date == "2023-06-20"
    assert wtbd.decision_to_ballot
    assert wtbd.majority_membership
    assert QualifyingCondition.GoodIndustrialRelations in wtbd.qualifying_conditions
    assert QualifyingCondition.EvidenceMembersOpposed in wtbd.qualifying_conditions
    assert (
        QualifyingCondition.MembershipEvidenceDoubts not in wtbd.qualifying_conditions
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-united-voices-of-the-world-ocs-group-uk-limited/whether-to-ballot-decision"
    ],
)
async def test_uvw_ocs_group(cac_document_contents):
    wtbd = await b.ExtractWhetherToBallotDecision(cac_document_contents)

    assert wtbd.decision_date == "2019-09-26"
    assert wtbd.decision_to_ballot
    assert not wtbd.majority_membership
    assert not wtbd.qualifying_conditions


@pytest.mark.parametrize(
    "url",
    [
        "https://assets.publishing.service.gov.uk/media/5ace298b40f0b617df33580d/Whether_to_Ballot_decision.pdf"
    ],
)
async def test_nuj_buzzfeed(cac_document_contents):
    wtbd = await b.ExtractWhetherToBallotDecision(cac_document_contents)

    assert wtbd.decision_date == "2018-04-11"
    assert wtbd.decision_to_ballot
    assert wtbd.majority_membership
    assert QualifyingCondition.GoodIndustrialRelations in wtbd.qualifying_conditions
    assert QualifyingCondition.EvidenceMembersOpposed not in wtbd.qualifying_conditions
    assert (
        QualifyingCondition.MembershipEvidenceDoubts not in wtbd.qualifying_conditions
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-neu-nasuwt-bishops-stortford-college/ballot-decision"
    ],
)
async def test_neu_bishops_stortford_college(cac_document_contents):
    wtbd = await b.ExtractWhetherToBallotDecision(cac_document_contents)

    assert wtbd.decision_date == "2020-11-09"
    assert wtbd.decision_to_ballot
    assert wtbd.majority_membership
    assert QualifyingCondition.GoodIndustrialRelations in wtbd.qualifying_conditions
    assert QualifyingCondition.EvidenceMembersOpposed not in wtbd.qualifying_conditions
    assert (
        QualifyingCondition.MembershipEvidenceDoubts not in wtbd.qualifying_conditions
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.gov.uk/government/publications/cac-outcome-unison-abbey-healthcare/whether-to-ballot-decision#considerations"
    ],
)
async def test_unison_abbey_healthcare(cac_document_contents):
    wtbd = await b.ExtractWhetherToBallotDecision(cac_document_contents)

    assert wtbd.decision_date == "2018-07-23"
    assert wtbd.decision_to_ballot
    assert not wtbd.majority_membership
    assert not wtbd.qualifying_conditions
