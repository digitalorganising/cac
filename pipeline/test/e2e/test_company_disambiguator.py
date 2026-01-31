import hashlib
import json

from . import invoke_lambda, indexer


async def test_company_disambiguator(opensearch_client):
    async with index_for_test("disambiguated-companies") as disambiguated_index:
        moreco = {
            "name": "Moreco Group Ltd",
            "unions": ["Unite the Union"],
            "application_date": "2025-11-27",
            "bargaining_unit": "All Moreco Group Ltd employees working at or from the Milk and More Watford Depot save for those employed at Assistant Manager Level or above",
            "locations": [
                "Milk and More Watford Depot (1 Odhams Trading Estate, Watford WD24 7RY)"
            ],
        }
        event = {"requests": [moreco]}

        results = await invoke_lambda("company_disambiguator", event)
