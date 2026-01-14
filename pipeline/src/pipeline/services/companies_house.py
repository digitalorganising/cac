import os
import json
import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx
from async_batcher.batcher import AsyncBatcher
from .secrets import secrets_store


def _get_api_key() -> Optional[str]:
    """Get Companies House API key from environment or secrets.

    Returns:
        API key string or None if not found
    """
    # Check environment variable first
    env_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    if env_key:
        return env_key

    # Check secrets manager
    secret_name = os.getenv("COMPANIES_HOUSE_API_KEY_SECRET")
    if secret_name:
        try:
            secret_string = secrets_store.get_secret_string(secret_name)
            secret_dict = json.loads(secret_string)
            return secret_dict.get("api_key") or secret_dict.get(
                "COMPANIES_HOUSE_API_KEY"
            )
        except Exception as e:
            print(f"Failed to get API key from secret {secret_name}: {e}")

    return None


# Fields to extract from company profile API
COMPANY_PROFILE_FIELDS = [
    "sic_codes",
    "date_of_cessation",
    "date_of_creation",
    "previous_company_names",
]

# Fields to allowlist from search API response
SEARCH_RESULT_ALLOWLIST = [
    "date_of_creation",
    "company_type",
    "company_number",
    "title",
    "address_snippet",
    "description",
]


@dataclass
class RateLimitState:
    """Tracks rate limit state from API headers."""

    limit: int = 600
    remaining: int = 600
    reset: int = 0  # Unix timestamp
    window: str = "5m"

    def update_from_headers(self, headers: Dict[str, str]) -> None:
        """Update rate limit state from response headers."""
        if "X-Ratelimit-Limit" in headers:
            self.limit = int(headers["X-Ratelimit-Limit"])
        if "X-Ratelimit-Remain" in headers:
            self.remaining = int(headers["X-Ratelimit-Remain"])
        if "X-Ratelimit-Reset" in headers:
            self.reset = int(headers["X-Ratelimit-Reset"])
        if "X-Ratelimit-Window" in headers:
            self.window = headers["X-Ratelimit-Window"]

    def time_until_reset(self) -> float:
        """Get seconds until rate limit resets."""
        if self.reset == 0:
            return 0.0
        now = time.time()
        return max(0.0, self.reset - now)

    def can_make_request(self, count: int = 1) -> bool:
        """Check if we can make the requested number of requests."""
        return self.remaining >= count

    async def wait_if_needed(self, count: int = 1) -> None:
        """Wait if we need to before making requests."""
        if not self.can_make_request(count):
            wait_time = self.time_until_reset()
            if wait_time > 0:
                print(
                    f"Rate limit reached ({self.remaining} remaining). "
                    f"Waiting {wait_time:.1f}s until reset..."
                )
                await asyncio.sleep(wait_time)
                # Reset remaining to limit after waiting
                self.remaining = self.limit


class CompanyProfileBatcher(AsyncBatcher[str, Dict[str, Any]]):
    """Batcher for fetching company profiles in parallel with rate limiting."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        auth: tuple,
        timeout: float,
        rate_limit: RateLimitState,
    ):
        """Initialize the company profile batcher.

        Args:
            client: httpx async client
            auth: Authentication tuple (api_key, "")
            timeout: Request timeout
            rate_limit: Shared rate limit state
        """
        # Configure batcher for rate limit: 600 requests per 5 minutes
        # Allow batching up to 50 requests, with 10 concurrent batches
        # This allows up to 500 concurrent requests, staying under the 600 limit
        super().__init__(
            max_batch_size=50,
            max_queue_time=0.5,  # Don't wait too long to batch
            concurrency=10,  # Allow 10 batches in parallel
        )
        self.client = client
        self.auth = auth
        self.timeout = timeout
        self.base_url = "https://api.company-information.service.gov.uk/company"
        self.rate_limit = rate_limit

    async def process_batch(self, batch: List[str]) -> List[Dict[str, Any]]:
        """Fetch company profiles for a batch of company numbers.

        Args:
            batch: List of company numbers

        Returns:
            List of company profile dictionaries with sic_codes
        """
        # Check rate limit before making requests
        await self.rate_limit.wait_if_needed(len(batch))

        # Fetch all company profiles in parallel
        tasks = [
            self._fetch_company_profile(company_number) for company_number in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle results and exceptions
        profiles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error fetching profile for {batch[i]}: {result}")
                profiles.append({})  # Return empty dict on error
            else:
                profiles.append(result)

        return profiles

    async def _fetch_company_profile(self, company_number: str) -> Dict[str, Any]:
        """Fetch a single company profile.

        Args:
            company_number: Company number to fetch

        Returns:
            Dictionary with requested fields from company profile
        """
        url = f"{self.base_url}/{company_number}"
        response = await self.client.get(
            url,
            auth=self.auth,
            timeout=self.timeout,
        )
        response.raise_for_status()

        # Update rate limit from response headers
        self.rate_limit.update_from_headers(dict(response.headers))

        profile = response.json()
        # Extract only requested fields
        return {field: profile.get(field) for field in COMPANY_PROFILE_FIELDS}


class CompaniesHouseClient:
    """Client for Companies House Search API.

    Uses the search API to find companies, then fetches company profiles
    in parallel to enrich results with SIC codes. Respects global rate limits
    via response headers.

    Documentation:
    - Search: https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/search/search-companies
    - Company Profile: https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/company-profile/company-profile
    """

    SEARCH_URL = "https://api.company-information.service.gov.uk/search/companies"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """Initialize the Companies House client.

        Args:
            api_key: Optional API key. If not provided, will attempt to get from
                    environment variable or secrets manager.
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self.api_key = api_key or _get_api_key()
        if not self.api_key:
            raise ValueError(
                "Companies House API key not found. "
                "Set COMPANIES_HOUSE_API_KEY environment variable or "
                "COMPANIES_HOUSE_API_KEY_SECRET secret name."
            )
        self.timeout = timeout
        # Companies House uses basic auth with the API key as the username
        # and an empty password
        self.auth = (self.api_key, "")
        # Shared rate limit state across all requests
        self.rate_limit = RateLimitState()

    async def search(
        self,
        q: str,
        items_per_page: int = 20,
        start_index: int = 0,
        restrictions: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for companies and enrich results with SIC codes.

        Args:
            q: The search term
            items_per_page: Number of results per page (default: 20)
            start_index: Starting index for pagination (default: 0)
            restrictions: Optional restrictions (space-separated)

        Returns:
            List of company items, where each item has been enriched with
            profile fields (sic_codes, date_of_cessation, previous_company_names)

        Raises:
            httpx.HTTPStatusError: If the API request fails
            httpx.RequestError: If there's a network error
        """
        # Build search parameters
        params: Dict[str, Any] = {
            "q": q,
            "items_per_page": items_per_page,
            "start_index": start_index,
        }
        if restrictions:
            params["restrictions"] = restrictions

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Check rate limit before search request
            await self.rate_limit.wait_if_needed(1)

            # Perform search
            response = await client.get(
                self.SEARCH_URL,
                auth=self.auth,
                params=params,
            )
            response.raise_for_status()

            # Update rate limit from search response headers
            self.rate_limit.update_from_headers(dict(response.headers))

            search_result = response.json()

            items = search_result.get("items", [])
            if not items:
                return []

            # Filter items to only include allowlisted fields
            filtered_items = []
            for item in items:
                filtered_item = {
                    field: item.get(field)
                    for field in SEARCH_RESULT_ALLOWLIST
                    if field in item
                }
                filtered_items.append(filtered_item)

            # Extract company numbers from filtered search results
            company_numbers = [
                item.get("company_number")
                for item in filtered_items
                if item.get("company_number")
            ]

            if not company_numbers:
                # Return filtered results even if no company numbers
                return filtered_items

            # Fetch company profiles in parallel using batcher
            batcher = CompanyProfileBatcher(
                client, self.auth, self.timeout, self.rate_limit
            )
            try:
                # Process all company numbers through the batcher
                profile_futures = [
                    batcher.process(company_number)
                    for company_number in company_numbers
                ]
                profiles = await asyncio.gather(*profile_futures)

                # Merge profile fields into filtered search results
                for item, profile in zip(filtered_items, profiles):
                    if profile:
                        for field in COMPANY_PROFILE_FIELDS:
                            item[field] = profile.get(field)
                    else:
                        # Set defaults for missing profiles
                        for field in COMPANY_PROFILE_FIELDS:
                            if field == "sic_codes":
                                item[field] = []
                            else:
                                item[field] = None

            finally:
                # Stop the batcher
                await batcher.stop(force=False)

            # Return filtered and enriched items
            return filtered_items
