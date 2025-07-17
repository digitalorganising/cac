import json
import logging
import tempfile
from typing import Optional

import crochet
from pydantic import BaseModel
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor
from scrapy.utils.log import configure_logging

from pipeline.spider import QuietDroppedLogFormatter, ReferencePipeline
from pipeline.spider.all_outcomes import AllOutcomesSpider
from pipeline.spider.cac_outcome_spider import CacOutcomeOpensearchPipeline

# Install the asyncio reactor for Lambda compatibility
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
crochet.setup()

logging.getLogger().handlers.clear()
log_settings = {
    "LOG_LEVEL": "INFO",
    "LOG_FORMATTER": QuietDroppedLogFormatter,
}
configure_logging(log_settings)


class ScraperEvent(BaseModel):
    indexSuffix: Optional[str] = None
    limitItems: Optional[int] = None


def handler(event, context):
    scraper_event = ScraperEvent.model_validate(event)
    index_suffix = scraper_event.indexSuffix
    index = f"outcomes-raw-{index_suffix}" if index_suffix else "outcomes-raw"

    @crochet.wait_for(timeout=60 * 60)  # More than the maximum possible lambda timeout
    def run_spider(outfile_path):
        settings = {
            "ITEM_PIPELINES": {
                CacOutcomeOpensearchPipeline: 100,
                ReferencePipeline: 200,
            },
            "CONCURRENT_ITEMS": 1,
            "OPENSEARCH": {
                "INDEX": index,
                "MAPPING_PATH": "./index_mappings/outcomes_raw.json",
            },
            "EXTENSIONS": {
                "scrapy.extensions.closespider.CloseSpider": 100,
            },
            "CLOSESPIDER_ITEMCOUNT": scraper_event.limitItems,
            "CLOSESPIDER_ERRORCOUNT": 5,
            "FEEDS": {
                outfile_path: {
                    "format": "json",
                    "overwrite": True,
                    "encoding": "utf-8",
                    "item_export_kwargs": {"separators": (",", ":")},
                },
            },
            **log_settings,
        }
        runner = CrawlerRunner(settings)
        return runner.crawl(AllOutcomesSpider)

    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8") as outfile:
        run_spider(outfile.name)
        outfile.seek(0)
        return json.load(outfile)
