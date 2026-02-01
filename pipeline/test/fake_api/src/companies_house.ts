import type { Context } from "hono";

export function searchCompanies(context: Context) {
  const query = context.req.query();

  let items: any[] = [];

  if (query.q?.toLowerCase().includes("wincanton")) {
    items.push({
      "kind": "searchresults#company",
      "description_identifier": [
        "incorporated-on"
      ],
      "company_status": "active",
      "date_of_creation": "2001-03-13",
      "company_type": "ltd",
      "company_number": "04178808",
      "address": {
        "address_line_2": "Methuen Park",
        "locality": "Chippenham",
        "postal_code": "SN14 0WT",
        "region": "Wiltshire"
      },
      "title": "WINCANTON LIMITED",
      "address_snippet": "Methuen Park, Chippenham, Wiltshire, SN14 0WT",
      "description": "04178808 - Incorporated on 13 March 2001",
      "links": {
        "self": "/company/04178808"
      },
      "snippet": "",
      "matches": {
        "snippet": []
      }
    },);
  }

  return context.json({
    total_results: items.length,
    items,
  });
}

export function getCompanyProfile(context: Context) {
  const companyNumber = context.req.param("company_number");

  if (!companyNumber) {
    return context.json({ error: "Company number is required" }, 400);
  }

  if (companyNumber === "04178808") {
    return context.json({
      "accounts": {
        "accounting_reference_date": {
          "day": "31",
          "month": "12"
        },
        "last_accounts": {
          "made_up_to": "2024-12-31",
          "period_end_on": "2024-12-31",
          "period_start_on": "2024-04-01",
          "type": "group"
        },
        "next_accounts": {
          "due_on": "2026-09-30",
          "overdue": false,
          "period_end_on": "2025-12-31",
          "period_start_on": "2025-01-01"
        },
        "next_due": "2026-09-30",
        "next_made_up_to": "2025-12-31",
        "overdue": false
      },
      "can_file": true,
      "company_name": "WINCANTON LIMITED",
      "company_number": "04178808",
      "company_status": "active",
      "confirmation_statement": {
        "last_made_up_to": "2025-12-31",
        "next_due": "2027-01-14",
        "next_made_up_to": "2026-12-31",
        "overdue": false
      },
      "date_of_creation": "2001-03-13",
      "etag": "7993db5f9b3918acc04a05afc51d46b754a80019",
      "has_been_liquidated": false,
      "has_charges": false,
      "has_insolvency_history": false,
      "jurisdiction": "england-wales",
      "last_full_members_list_date": "2011-03-13",
      "links": {
        "persons_with_significant_control": "/company/04178808/persons-with-significant-control",
        "self": "/company/04178808",
        "filing_history": "/company/04178808/filing-history",
        "officers": "/company/04178808/officers",
        "exemptions": "/company/04178808/exemptions"
      },
      "previous_company_names": [
        {
          "ceased_on": "2024-06-19",
          "effective_from": "2001-03-13",
          "name": "WINCANTON PLC"
        }
      ],
      "registered_office_address": {
        "address_line_2": "Methuen Park",
        "locality": "Chippenham",
        "postal_code": "SN14 0WT",
        "region": "Wiltshire"
      },
      "registered_office_is_in_dispute": false,
      "sic_codes": [
        "49410",
        "52103",
        "52219",
        "52243"
      ],
      "type": "ltd",
      "undeliverable_registered_office_address": false,
      "has_super_secure_pscs": false
    });
  }

  context.status(404);
  return context.json({ error: "Company not found" });
}
