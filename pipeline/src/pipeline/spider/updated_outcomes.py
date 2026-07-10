import httpx
from typing import Optional
from datetime import datetime
from scrapy import Request

from .. import london_date
from ..transforms.events_machine import unterminated_states, terminal_states
from .cac_outcome_spider import CacOutcomeSpider


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
    def force_last_event(self):
        str_date = self.outcomes_settings.get("FORCE_LAST_EVENT")
        return london_date(str_date) if str_date else None

    async def get_last_event(self):
        if self.force_last_event:
            return self.force_last_event
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                params = {
                    "state": ",".join([t.value for t in terminal_states]),
                    "sort": "lastEvent-desc",
                }
                response = await client.get(f"{self.api_base}/outcomes", params=params)
                response.raise_for_status()
                data = response.json()
                return london_date(data["outcomes"][0]["keyDates"]["lastEvent"])
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
                            "lastEvent": london_date(outcome["keyDates"]["lastEvent"]),
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

    def request_year_list(self, year: int, last_event: datetime):
        return Request(
            url=(self.list_url_prefix + str(year)),
            cb_kwargs={"last_event": last_event, "this_year": year},
            callback=self.updated_outcomes_from_list,
        )

    async def start(self):
        last_event = await self.get_last_event()
        n_unterminated_outcomes = 0
        async for outcome in self.get_unterminated_outcomes():
            yield Request(url=outcome["cacUrl"])
            n_unterminated_outcomes += 1
        self.logger.info(
            f"Checking for updates in {n_unterminated_outcomes} unterminated outcomes"
        )

        self.logger.info(f"Looking for outcomes with events since {last_event}")
        yield self.request_year_list(last_event.year, last_event)

    def updated_outcomes_from_list(self, response, last_event, this_year):
        outcome_list_items = response.css(
            "h3#trade-union-recognition + " "div + div > ul > li"
        )
        for outcome_list_item in outcome_list_items:
            outcome_link = outcome_list_item.css("div a")
            outcome_url = response.urljoin(outcome_link.attrib["href"])
            outcome_last_updated = london_date(
                outcome_list_item.css("ul time::attr(datetime)").get()
            )
            if outcome_last_updated >= last_event:
                yield Request(url=outcome_url)

        maybe_next_year = this_year + 1
        yield self.request_year_list(maybe_next_year, last_event)
