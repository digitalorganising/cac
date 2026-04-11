from . import invoke_lambda, indexer
from company_disambiguator.model import request_to_doc_id, DisambiguateCompanyRequest

moreco = {
    "name": "Moreco Group Ltd",
    "unions": ["Unite the Union"],
    "application_date": "2025-11-27",
    "bargaining_unit": "All Moreco Group Ltd employees working at or from the Milk and More Watford Depot save for those employed at Assistant Manager Level or above",
    "locations": [
        "Milk and More Watford Depot (1 Odhams Trading Estate, Watford WD24 7RY)"
    ],
}

wincanton = {
    "name": "Wincanton Ltd",
    "unions": ["Unite the Union"],
    "application_date": "2025-11-03",
    "bargaining_unit": "Transport Clerical (AT4’s), M grade managers (M1 Grade Managers)",
    "locations": ["Sainsbury’s Basingstoke, Houndmills Rd, Basingstoke, RG21 6XW"],
}

british_academy = {
    "name": "The British Academy for the Promotion of Historical Philosophical and Philological Studies (The British Academy)",
    "unions": ["Prospect"],
    "application_date": "2024-03-08",
    "bargaining_unit": "all employees of the British Academy, except Directors and the Head of HR",
    "locations": ["10-11 Carlton House Terrace, London, SW1Y 5AH"],
}

initial_docs = [
    {
        "id": request_to_doc_id(DisambiguateCompanyRequest(**moreco)),
        "input": moreco,
        "disambiguated_company": {
            "company_name": "Moreco Group Ltd",
            "type": "identified",
            "company_number": "13537233",
            "industrial_classifications": [
                {
                    "sic_code": "47910",
                    "description": "Retail sale of food in non-specialised retail shops",
                    "section": "Retail trade",
                }
            ],
        },
    }
]


async def test_company_disambiguator(opensearch_client):
    index_for_test = indexer(opensearch_client)
    async with index_for_test(
        "disambiguated-companies", no_suffix=True, initial_docs=initial_docs
    ):
        r0 = await invoke_lambda("company_disambiguator", {**moreco, "force": False})
        r1 = await invoke_lambda("company_disambiguator", {**wincanton, "force": False})
        r2 = await invoke_lambda(
            "company_disambiguator", {**british_academy, "force": False}
        )

        results = await opensearch_client.search(index="disambiguated-companies")
        hits = results["hits"]["hits"]
        assert len(hits) == 3

        doc0 = next(h for h in hits if h["_id"] == r0["_id"])["_source"][
            "disambiguated_company"
        ]
        doc1 = next(h for h in hits if h["_id"] == r1["_id"])["_source"][
            "disambiguated_company"
        ]
        doc2 = next(h for h in hits if h["_id"] == r2["_id"])["_source"][
            "disambiguated_company"
        ]
        assert doc0 == {
            "company_name": "Moreco Group Ltd",
            "company_number": "13537233",
            "industrial_classifications": [
                {
                    "description": "Retail sale of food in non-specialised retail shops",
                    "section": "Retail trade",
                    "sic_code": "47910",
                }
            ],
            "type": "identified",
        }

        assert doc1 == {
            "company_name": "Wincanton Ltd",
            "company_number": "04178808",
            "industrial_classifications": [
                {
                    "description": "Freight transport by road",
                    "section": "Transportation and storage",
                    "sic_code": "49410",
                },
                {
                    "description": "Operation of warehousing and storage facilities for land transport activities",
                    "section": "Transportation and storage",
                    "sic_code": "52103",
                },
                {
                    "description": "Other service activities incidental to land transportation, n.e.c.",
                    "section": "Transportation and storage",
                    "sic_code": "52219",
                },
                {
                    "description": "Cargo handling for land transport activities",
                    "section": "Transportation and storage",
                    "sic_code": "52243",
                },
            ],
            "type": "identified",
        }

        assert doc2 == {
            "company_name": "The British Academy for the Promotion of Historical Philosophical and Philological Studies (The British Academy)",
            "type": "unidentified",
            "subtype": "Charity",
            "industrial_classifications": [],
        }
