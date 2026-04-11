import os
from opensearchpy.exceptions import NotFoundError

from pipeline.services.opensearch_utils import (
    ensure_index_mapping,
    get_mapping_from_path,
)
from company_disambiguator.companies_house import CompaniesHouseClient
from company_disambiguator.model import (
    DisambiguateCompanyLambdaEvent,
    StoredResult,
    request_to_doc_id,
)
from company_disambiguator.pipeline import (
    disambiguate_company,
    upsert_stored_result,
)
from . import lambda_friendly_run_async, client, DocumentRef


OPENSEARCH_INDEX = "disambiguated-companies"

companies_house_client = CompaniesHouseClient(base_url=os.getenv("CH_API_BASE"))


def stored_result_to_ref(stored: StoredResult) -> DocumentRef:
    return DocumentRef(
        _id=stored.id,
        _index=OPENSEARCH_INDEX,
    ).model_dump(by_alias=True)


async def process_request(event: DisambiguateCompanyLambdaEvent):
    index_mapping = get_mapping_from_path(
        "./index_mappings/disambiguated_companies.json"
    )
    await ensure_index_mapping(client, OPENSEARCH_INDEX, index_mapping)

    request = event.without_force()
    disambiguation_id = request_to_doc_id(request)

    if not event.force:
        try:
            res = await client.get(index=OPENSEARCH_INDEX, id=disambiguation_id)
            stored = StoredResult.model_validate(res["_source"])
            return stored_result_to_ref(stored)
        except NotFoundError:
            pass

    disambiguated, debug = await disambiguate_company(request, companies_house_client)
    stored = await upsert_stored_result(
        client,
        OPENSEARCH_INDEX,
        StoredResult(
            id=disambiguation_id,
            disambiguated_company=disambiguated,
            input=request,
            debug=debug,
        ),
    )
    return stored_result_to_ref(stored)


def handler(event, context):
    payload = DisambiguateCompanyLambdaEvent.model_validate(event)
    return lambda_friendly_run_async(process_request(payload))
