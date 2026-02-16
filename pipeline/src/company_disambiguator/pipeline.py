"""Operations for disambiguated companies: storage, retrieval, and indexing."""

import json
import os
from typing import Optional

from opensearchpy import AsyncOpenSearch, helpers

from pipeline.services.baml import authenticated_client
from company_disambiguator.companies_house import CompaniesHouseClient
from company_disambiguator.model import (
    DisambiguateCompanyRequest,
    DisambiguatedCompany,
    StoredResult,
    request_to_doc_id,
)
from company_disambiguator.sic_codes import transform_baml_result
from baml_client.types import UnidentifiedCompany as BamlUnidentifiedCompany


baml_options = {}
if os.getenv("MOCK_LLM"):
    baml_options["client"] = "FakeApiClient"


async def get_stored_companies(
    client: AsyncOpenSearch,
    index: str,
    requests: list[DisambiguateCompanyRequest],
) -> dict[str, DisambiguatedCompany]:
    """Fetch stored companies for multiple requests using mget.

    Args:
        client: OpenSearch client
        index: Index name
        requests: List of requests to check

    Returns:
        Dictionary mapping doc_id to stored result (only for found documents)
    """
    if not requests:
        return {}

    # Generate doc IDs for all requests
    doc_ids = [request_to_doc_id(req) for req in requests]

    # Use mget to fetch all documents at once
    # mget preserves order, so results are in the same order as doc_ids
    mget_response = await client.mget(
        body={"docs": [{"_index": index, "_id": doc_id} for doc_id in doc_ids]}
    )

    # Convert found documents to results using Pydantic validation
    # Build dict in order to preserve doc_id -> result mapping
    stored_results: dict[str, DisambiguatedCompany] = {}
    for doc in mget_response["docs"]:
        if doc.get("found"):
            stored = StoredResult.model_validate(doc["_source"])
            stored_results[doc["_id"]] = stored.disambiguated_company

    return stored_results


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
    # Search for candidate companies using the name
    candidates = await companies_house_client.search(
        q=request.name,
        items_per_page=5,
    )

    # Convert candidates list to JSON string
    candidates_json = json.dumps(candidates)

    # Call BAML function with candidates and other parameters
    baml_result = await authenticated_client.DisambiguateCompany(
        candidates=candidates_json,
        name=request.name,
        unions=request.unions,
        application_date=request.application_date,
        bargaining_unit=request.bargaining_unit,
        locations=request.locations,
        baml_options=baml_options,
    )

    # Transform result (sic_codes -> industrial_classifications)
    transformed = transform_baml_result(baml_result, request.name)

    debug = None
    if baml_result and isinstance(baml_result, BamlUnidentifiedCompany):
        debug = {"reason": baml_result.reason}

    return transformed, debug


async def bulk_index_results(
    client: AsyncOpenSearch, index: str, docs: list[StoredResult]
) -> None:
    """Bulk index disambiguation results.

    Args:
        client: OpenSearch client
        index: Index name
        docs: List of StoredResult objects to index
    """

    # Generate index actions
    async def index_actions():
        for doc in docs:
            doc_id = doc.id
            stored_result = doc
            yield {
                "_op_type": "update",
                "_index": index,
                "_id": doc_id,
                "doc": stored_result.model_dump(exclude_none=True),
                "doc_as_upsert": True,
            }

    # Bulk index all documents
    async for ok, result in helpers.async_streaming_bulk(
        client, index_actions(), index=index
    ):
        if not ok:
            raise Exception("Failed to index item", result)

    # Refresh index after bulk operation
    await client.indices.refresh(index=index)
