"""Operations for disambiguated companies: storage, retrieval, and indexing."""

import json
import logging
import os
from typing import Optional

from opensearchpy import AsyncOpenSearch

from pipeline.services.baml import authenticated_client
from company_disambiguator.companies_house import CompaniesHouseClient
from company_disambiguator.model import (
    DisambiguateCompanyRequest,
    DisambiguatedCompany,
    IdentifiedCompany,
    UnidentifiedCompany,
    StoredResult,
)
from company_disambiguator.sic_codes import transform_sic_codes


baml_options = {}
if os.getenv("MOCK_LLM"):
    baml_options["client"] = "FakeApiClient"


async def disambiguate_company(
    request: DisambiguateCompanyRequest,
    companies_house_client: CompaniesHouseClient,
) -> tuple[DisambiguatedCompany, Optional[dict[str, str]]]:
    """Disambiguate a single company.

    Args:
        request: Disambiguation request
        companies_house_client: Companies House client instance

    Returns:
        Tuple of (transformed result, optional debug info)
    """

    async def disambiguate_for_name(company_name: str):
        # Search for candidate companies using the name
        candidates = await companies_house_client.search(
            q=company_name,
            items_per_page=5,
        )
        filtered_candidates = [c for c in candidates if c["sic_codes"]]

        # Convert candidates list to JSON string
        candidates_json = json.dumps(filtered_candidates)

        # Call BAML function with candidates and other parameters
        return (
            await authenticated_client.DisambiguateCompany(
                candidates=candidates_json,
                name=company_name,
                unions=request.unions,
                application_date=request.application_date,
                bargaining_unit=request.bargaining_unit,
                locations=request.locations,
                baml_options=baml_options,
            ),
            filtered_candidates,
        )

    debug = None
    suggested_name = None
    baml_result, candidates = await disambiguate_for_name(request.name)
    if baml_result.type == "requires-new-search":
        logging.info(f"New search required for {request.name}: {baml_result.reason}")
        debug = {
            "reason": baml_result.reason,
            "new_search": baml_result.suggested_name,
            "original_candidates": [c["title"] for c in candidates],
        }
        suggested_name = baml_result.suggested_name
        baml_result, candidates = await disambiguate_for_name(suggested_name)

    if baml_result.type == "requires-new-search":
        debug = {
            **debug,
            "reason_2": baml_result.reason,
            "new_search_2": baml_result.suggested_name,
            "new_search_candidates": [c["title"] for c in candidates],
        }

        baml_result = await authenticated_client.GuessSicCodes(
            name=request.name,
            unions=request.unions,
            bargaining_unit=request.bargaining_unit,
            locations=request.locations,
            baml_options=baml_options,
        )

    sic_codes = []
    if hasattr(baml_result, "sic_codes"):
        sic_codes = baml_result.sic_codes
    else:
        for candidate in candidates:
            if candidate["company_number"] == baml_result.company_number:
                sic_codes = candidate["sic_codes"]
                break

    industrial_classifications = transform_sic_codes(sic_codes)
    if baml_result.type == "identified":
        result = IdentifiedCompany(
            type="identified",
            company_name=request.name,
            company_number=baml_result.company_number,
            industrial_classifications=industrial_classifications,
        )
    elif baml_result.type == "unidentified":
        result = UnidentifiedCompany(
            type="unidentified",
            subtype=baml_result.subtype,
            company_name=request.name,
            industrial_classifications=industrial_classifications,
        )
    else:
        raise RuntimeError(f"You should never see this error! ({request.name})")

    return result, debug


async def upsert_stored_result(
    client: AsyncOpenSearch,
    index: str,
    stored: StoredResult,
) -> StoredResult:
    await client.update(
        index=index,
        id=stored.id,
        body={
            "doc": stored.model_dump(exclude_none=True),
            "doc_as_upsert": True,
        },
        params={"retry_on_conflict": 3},
    )
    await client.indices.refresh(index=index)
    return stored
