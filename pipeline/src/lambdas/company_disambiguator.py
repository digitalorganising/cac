import asyncio
import os
from typing import List

from pipeline.services.opensearch_utils import (
    ensure_index_mapping,
    get_mapping_from_path,
)
from company_disambiguator.companies_house import CompaniesHouseClient
from company_disambiguator.model import (
    DisambiguateCompanyRequest,
    DisambiguateCompanyEvent,
    DisambiguatedCompany,
    StoredResult,
    request_to_doc_id,
)
from company_disambiguator.pipeline import (
    bulk_index_results,
    disambiguate_company,
    get_stored_companies,
)
from . import lambda_friendly_run_async, client, gather_with_concurrency


# OpenSearch index name
OPENSEARCH_INDEX = "disambiguated-companies"

companies_house_client = CompaniesHouseClient(base_url=os.getenv("CH_API_BASE"))


async def process_batch(requests: List[DisambiguateCompanyRequest]):
    """Process a batch of disambiguation requests.

    Args:
        requests: List of disambiguation requests

    Returns:
        List of disambiguation results with industrial_classifications instead of sic_codes
    """
    # Ensure index mapping exists
    index_mapping = get_mapping_from_path(
        "./index_mappings/disambiguated_companies.json"
    )
    await ensure_index_mapping(client, OPENSEARCH_INDEX, index_mapping)

    # Step 1: Get all stored companies in one mget call
    stored_results = await get_stored_companies(client, OPENSEARCH_INDEX, requests)

    # Step 2: Identify which requests need processing
    doc_ids = [request_to_doc_id(req) for req in requests]
    stored_by_request = [stored_results.get(doc_id) for doc_id in doc_ids]

    requests_to_process = [
        req for req, stored in zip(requests, stored_by_request) if stored is None
    ]

    # Step 3: Process unstored requests in parallel
    # asyncio.gather preserves order, so new_results matches requests_to_process order
    new_results: List[DisambiguatedCompany] = []
    if requests_to_process:
        disambiguation_results = await gather_with_concurrency(
            [
                disambiguate_company(req, companies_house_client)
                for req in requests_to_process
            ],
            max_concurrent=3,
        )
        new_results = [result[0] for result in disambiguation_results]
        debug_info = [result[1] for result in disambiguation_results]

        # Step 4: Create StoredResult objects and bulk index
        stored_docs = [
            StoredResult(
                disambiguated_company=result,
                input=request,
                debug=debug,
            )
            for request, result, debug in zip(
                requests_to_process, new_results, debug_info
            )
        ]
        await bulk_index_results(client, OPENSEARCH_INDEX, stored_docs)

    # Step 5: Combine stored and new results in original order
    new_result_iter = iter(new_results)
    results = [
        (
            stored.model_dump(exclude_none=True)
            if stored is not None
            else next(new_result_iter).model_dump(exclude_none=True)
        )
        for stored in stored_by_request
    ]

    return results


def handler(event, context):
    """Lambda handler for company disambiguation."""
    disambiguator_event = DisambiguateCompanyEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(disambiguator_event.requests))
