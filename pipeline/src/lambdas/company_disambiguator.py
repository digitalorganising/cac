import os

from pipeline.services.opensearch_utils import (
    ensure_index_mapping,
    get_mapping_from_path,
)
from company_disambiguator.companies_house import CompaniesHouseClient
from company_disambiguator.model import (
    DisambiguateCompanyLambdaEvent,
    StoredResult,
)
from company_disambiguator.pipeline import (
    disambiguate_company,
    get_stored_company,
    upsert_stored_result,
)
from . import lambda_friendly_run_async, client


OPENSEARCH_INDEX = "disambiguated-companies"

companies_house_client = CompaniesHouseClient(base_url=os.getenv("CH_API_BASE"))


async def process_request(event: DisambiguateCompanyLambdaEvent):
    index_mapping = get_mapping_from_path(
        "./index_mappings/disambiguated_companies.json"
    )
    await ensure_index_mapping(client, OPENSEARCH_INDEX, index_mapping)

    request = event.without_force()

    if not event.force:
        stored = await get_stored_company(client, OPENSEARCH_INDEX, request)
        if stored is not None:
            return stored.model_dump(exclude_none=True)

    disambiguated, debug = await disambiguate_company(request, companies_house_client)
    await upsert_stored_result(
        client,
        OPENSEARCH_INDEX,
        StoredResult(
            disambiguated_company=disambiguated,
            input=request,
            debug=debug,
        ),
    )
    return disambiguated.model_dump(exclude_none=True)


def handler(event, context):
    payload = DisambiguateCompanyLambdaEvent.model_validate(event)
    return lambda_friendly_run_async(process_request(payload))
