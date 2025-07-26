import httpx
from typing import Optional
from datetime import datetime
from dateutil.tz import gettz
from dateutil.parser import parse as date_parse
from dateutil.utils import default_tzinfo
from scrapy import Request

from ..transforms.events_machine import unterminated_states
from .cac_outcome_spider import CacOutcomeSpider


def london_date(date_str: str):
    london_tz = gettz("Europe/London")
    return default_tzinfo(date_parse(date_str), london_tz)


class UpdatedOutcomesSpider(CacOutcomeSpider):
    name = "cac-outcomes"

    @property
    def outcomes_settings(self):
        return self.settings.get("OUTCOMES", {})

    @property
    def api_base(self):
        return self.outcomes_settings.get("API_BASE")

    @property
    def start_date(self):
        str_date = self.outcomes_settings.get("START_DATE")
        return london_date(str_date) if str_date else None

    @property
    def unterminated_outcomes_age_limit(self):
        return self.outcomes_settings.get("UNTERMINATED_OUTCOMES_AGE_LIMIT")

    @property
    def force_last_updated(self):
        str_date = self.outcomes_settings.get("FORCE_LAST_UPDATED")
        return london_date(str_date) if str_date else None

    async def get_last_updated(self):
        if self.force_last_updated:
            return self.force_last_updated
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(f"{self.api_base}/outcomes")
                response.raise_for_status()
                data = response.json()
                return london_date(data["outcomes"][0]["lastUpdated"])
            except (httpx.HTTPStatusError, KeyError) as e:
                return self.start_date

    async def get_unterminated_outcomes(self):
        async with httpx.AsyncClient(timeout=10) as client:

            async def get_outcomes(url: str, params: Optional[dict] = None):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    for outcome in data["outcomes"]:
                        yield {
                            "reference": outcome["reference"],
                            "cacUrl": outcome["cacUrl"],
                            "lastUpdated": london_date(outcome["lastUpdated"]),
                        }
                    if data.get("nextPage"):
                        async for outcome in get_outcomes(data["nextPage"]):
                            yield outcome
                except (httpx.HTTPStatusError, KeyError):
                    return

            params = {"state": ",".join([t.value for t in unterminated_states])}
            if self.unterminated_outcomes_age_limit:
                params["events.date.from"] = (
                    datetime.now() - self.unterminated_outcomes_age_limit
                ).strftime("%Y-%m-%d")
            async for outcome in get_outcomes(f"{self.api_base}/outcomes", params):
                yield outcome

    def request_year_list(self, year: int, last_updated: datetime):
        return Request(
            url=(self.list_url_prefix + str(year)),
            cb_kwargs={"last_updated": last_updated, "this_year": year},
            callback=self.updated_outcomes_from_list,
        )

    async def start(self):
        last_updated = await self.get_last_updated()
        n_unterminated_outcomes = 0
        async for outcome in self.get_unterminated_outcomes():
            yield Request(url=outcome["cacUrl"])
            n_unterminated_outcomes += 1
        self.logger.info(
            f"Checking for updates in {n_unterminated_outcomes} unterminated outcomes"
        )

        self.logger.info(f"Looking for outcomes updated since {last_updated}")
        yield self.request_year_list(last_updated.year, last_updated)

    def updated_outcomes_from_list(self, response, last_updated, this_year):
        outcome_list_items = response.css(
            "h3#trade-union-recognition + " "div + div > ul > li"
        )
        for outcome_list_item in outcome_list_items:
            outcome_link = outcome_list_item.css("div a")
            outcome_url = response.urljoin(outcome_link.attrib["href"])
            outcome_last_updated = london_date(
                outcome_list_item.css("ul time::attr(datetime)").get()
            )
            if outcome_last_updated >= last_updated:
                yield Request(url=outcome_url)

        maybe_next_year = this_year + 1
        yield self.request_year_list(maybe_next_year, last_updated)
