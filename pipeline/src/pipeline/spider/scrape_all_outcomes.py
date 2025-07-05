from scrapy import Request
from scrapy.crawler import CrawlerProcess

from . import QuietDroppedLogFormatter
from .cac_outcome_spider import CacOutcomeSpider, CacOutcomeOpensearchPipeline


class AllOutcomesSpider(CacOutcomeSpider):
    name = "cac-outcomes"
    start_year = 2014

    async def start(self):
        yield Request(
            url=(self.list_url_prefix + str(self.start_year)),
            meta={"year": self.start_year},
            callback=self.parse_outcomes_list,
        )

    def parse_outcomes_list(self, response):
        outcome_links = response.css(
            "h3#trade-union-recognition + " "div + div > ul > li div a"
        )
        yield from response.follow_all(urls=outcome_links)

        maybe_next_year = response.meta["year"] + 1
        yield response.follow(
            url=(self.list_url_prefix + str(maybe_next_year)),
            meta={"year": maybe_next_year},
            callback=self.parse_outcomes_list,
        )


def scrape():
    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "INFO",
            "LOG_FORMATTER": QuietDroppedLogFormatter,
            "ITEM_PIPELINES": {CacOutcomeOpensearchPipeline: 100},
            "CONCURRENT_ITEMS": 10,
            "OPENSEARCH": {
                "INDEX": "outcomes-raw-20250624",
                "MAPPING_PATH": "./pipeline/index_mappings/outcomes_raw.json",
            },
        }
    )
    process.crawl(AllOutcomesSpider)
    process.start()


if __name__ == "__main__":
    scrape()
