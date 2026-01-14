#!/usr/bin/env python3
"""Command-line script to search Companies House and get company details with SIC codes."""

import argparse
import asyncio
import json
import sys

from pipeline.services.companies_house import CompaniesHouseClient

parser = argparse.ArgumentParser(
    description="Search Companies House and enrich results with SIC codes"
)
parser.add_argument(
    "query",
    type=str,
    help="Search query term",
)
parser.add_argument(
    "--items-per-page",
    type=int,
    default=5,
    help="Number of results per page (default: 20)",
)
parser.add_argument(
    "--start-index",
    type=int,
    default=0,
    help="Starting index for pagination (default: 0)",
)
parser.add_argument(
    "--restrictions",
    type=str,
    help="Restrictions (space-separated, e.g., 'active-companies legally-equivalent-company-name')",
)
parser.add_argument(
    "--json",
    action="store_true",
    help="Output raw JSON instead of formatted text",
)
args = parser.parse_args()


async def main():
    """Run the Companies House search."""
    try:
        client = CompaniesHouseClient()
        result = await client.search(
            q=args.query,
            items_per_page=args.items_per_page,
            start_index=args.start_index,
            restrictions=args.restrictions,
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            # Pretty print
            items = result
            print(f"\nSearch Results for: '{args.query}'")
            print(f"Found {len(items)} result(s)")
            print("-" * 80)

            for i, item in enumerate(items, 1):
                company_number = item.get("company_number", "N/A")
                company_name = item.get("title", "N/A")
                company_status = item.get("company_status", "N/A")
                sic_codes = item.get("sic_codes", [])
                address = item.get("address_snippet", "N/A")
                date_of_creation = item.get("date_of_creation")
                date_of_cessation = item.get("date_of_cessation")
                previous_company_names = item.get("previous_company_names")

                print(f"\n{i}. {company_name}")
                print(f"   Company Number: {company_number}")
                print(f"   Status: {company_status}")
                print(f"   Address: {address}")
                if date_of_creation:
                    print(f"   Date of Creation: {date_of_creation}")
                if date_of_cessation:
                    print(f"   Date of Cessation: {date_of_cessation}")
                if sic_codes:
                    print(f"   SIC Codes: {', '.join(str(code) for code in sic_codes)}")
                else:
                    print("   SIC Codes: None")
                if previous_company_names:
                    # previous_company_names is a list of objects with 'name' and 'ceased_on' fields
                    names = [
                        f"{name.get('name', 'N/A')} (ceased: {name.get('ceased_on', 'N/A')})"
                        for name in previous_company_names
                    ]
                    print(f"   Previous Company Names: {', '.join(names)}")

            print("\n" + "-" * 80)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
