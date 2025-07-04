import httpx
from itemadapter import ItemAdapter
from typing import Optional, override
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from . import QuietDroppedLogFormatter
from ..transforms.events_machine import unterminated_states
from .cac_outcome_spider import CacOutcomeSpider, CacOutcomeOpensearchPipeline


class DedupingPipeline(CacOutcomeOpensearchPipeline):
    async def maybe_requires_update(self, item):
        document_type = item["document_type"]
        id = self.id(item)
        fingerprint = self.fingerprint(item)

        res = await self.client.search(
            index=self.index,
            body={
                "size": 1,
                "terminate_after": 1,
                "query": {
                    "bool": {
                        "filter": [{"term": {"reference": id}}],
                        "must_not": [
                            {
                                "term": {
                                    f"document_fingerprints.{document_type}": fingerprint
                                }
                            }
                        ],
                    },
                },
            },
        )
        return res["hits"]["total"]["value"] != 0

    @override
    async def skip_item(self, item):
        if await super().skip_item(item):
            return True

        requires_update = await self.maybe_requires_update(item)
        return not requires_update


class UpdatedOutcomesSpider(CacOutcomeSpider):
    name = "updated-cac-outcomes"
    api_base = "http://localhost:3000/api"
    # api_base = "https://cac.digitalorganis.ing/api"

    async def get_unterminated_outcomes(self, age_limit: Optional[timedelta] = None):
        async with httpx.AsyncClient(timeout=10) as client:

            async def get_outcomes(url: str, params: Optional[dict] = None):
                response = await client.get(url, params=params)
                data = response.json()
                for outcome in data["outcomes"]:
                    yield {
                        "reference": outcome["reference"],
                        "cacUrl": outcome["cacUrl"],
                        "lastUpdated": date_parse(outcome["lastUpdated"]),
                    }
                if data.get("nextPage"):
                    async for outcome in get_outcomes(data["nextPage"]):
                        yield outcome

            params = {"state": ",".join([t.value for t in unterminated_states])}
            if age_limit:
                params["events.date.from"] = (datetime.now() - age_limit).strftime(
                    "%Y-%m-%d"
                )
            async for outcome in get_outcomes(f"{self.api_base}/outcomes", params):
                yield outcome

    async def start(self):
        last_updated = None
        async for outcome in self.get_unterminated_outcomes():
            last_updated = (
                max(last_updated, outcome["lastUpdated"])
                if last_updated
                else outcome["lastUpdated"]
            )
            yield Request(url=outcome["cacUrl"])

        now_year = datetime.now().year
        last_updated_year = last_updated.year if last_updated else now_year

        yield Request(
            url=(self.list_url_prefix + str(last_updated_year)),
            cb_kwargs={"last_updated": last_updated},
            callback=self.updated_outcomes_from_list,
        )

        if last_updated_year < now_year:
            yield Request(
                url=(self.list_url_prefix + str(now_year)),
                cb_kwargs={"last_updated": last_updated},
                callback=self.updated_outcomes_from_list,
            )

    def updated_outcomes_from_list(self, response, last_updated):
        outcome_list_items = response.css(
            "h3#trade-union-recognition + " "div + div > ul > li"
        )
        for outcome_list_item in outcome_list_items:
            outcome_link = outcome_list_item.css("div a")
            outcome_url = response.urljoin(outcome_link.attrib["href"])
            outcome_last_updated = date_parse(
                outcome_list_item.css("ul time::attr(datetime)").get()
            )
            if outcome_last_updated >= last_updated:
                yield Request(url=outcome_url)


def scrape():
    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "INFO",
            "LOG_FORMATTER": QuietDroppedLogFormatter,
            "ITEM_PIPELINES": {DedupingPipeline: 100},
            "CONCURRENT_ITEMS": 2,  # The pessimistic checking requires a lot of requests
            "OPENSEARCH": {
                "INDEX": "outcomes-raw-20250624",
                "MAPPING_PATH": "./pipeline/index_mappings/outcomes_raw.json",
            },
        }
    )
    process.crawl(UpdatedOutcomesSpider)
    process.start()


if __name__ == "__main__":
    scrape()
