import logging
import os
from datetime import timedelta
from typing import Optional

import crochet
from pydantic import BaseModel
from opensearchpy import helpers
from scrapy.crawler import CrawlerRunner, Crawler
from scrapy.utils.reactor import install_reactor
from scrapy.utils.log import configure_logging
from scrapy import signals

from pipeline.spider import QuietDroppedLogFormatter
from pipeline.spider.updated_outcomes import UpdatedOutcomesSpider
from pipeline.spider.cac_outcome_spider import CacOutcomeOpensearchPipeline
from pipeline.types.decisions import decision_raw_mapping

from . import client, lambda_friendly_run_async

# Install the asyncio reactor for Lambda compatibility
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
crochet.setup()

logging.getLogger().handlers.clear()
log_settings = {
    "LOG_LEVEL": "INFO",
    "LOG_FORMATTER": QuietDroppedLogFormatter,
}
configure_logging(log_settings)


class Redrive(BaseModel):
    complete: bool = False
    augment: bool = True
    ids: Optional[list[str]] = None


class ScraperEvent(BaseModel):
    indexSuffix: Optional[str] = None
    limitItems: Optional[int] = None
    forceLastUpdated: Optional[str] = None
    redrive: Optional[Redrive] = None


def int_env(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def do_redrive(redrive: Redrive, index: str):
    if redrive.ids and not redrive.complete:
        return [
            {"_id": id, "_index": index, "passthrough": not redrive.augment}
            for id in redrive.ids
        ]
    if redrive.complete:

        async def get_all_refs():
            refs = []
            async for doc in helpers.async_scan(client, index=index, size=20):
                refs.append(
                    {
                        "_id": doc["_id"],
                        "_index": doc["_index"],
                        "passthrough": not redrive.augment,
                    }
                )
            return refs

        return lambda_friendly_run_async(get_all_refs())


def handler(event, context):
    scraper_event = ScraperEvent.model_validate(event)
    index_suffix = scraper_event.indexSuffix
    index = f"outcomes-raw-{index_suffix}" if index_suffix else "outcomes-raw"

    if scraper_event.redrive:
        return do_redrive(scraper_event.redrive, index)

    references = []

    def add_ref(item):
        id = CacOutcomeOpensearchPipeline.id(None, item)
        references.append(
            {
                "_id": id,
                "_index": index,
            }
        )

    @crochet.wait_for(timeout=60 * 60)  # More than the maximum possible lambda timeout
    def run_spider():
        age_limit_days = int_env("UNTERMINATED_OUTCOMES_AGE_LIMIT_DAYS")
        settings = {
            "ITEM_PIPELINES": {
                CacOutcomeOpensearchPipeline: 100,
            },
            "OUTCOMES": {
                "API_BASE": os.getenv("API_BASE"),
                "START_DATE": "2014-01-01",
                "UNTERMINATED_OUTCOMES_AGE_LIMIT": (
                    timedelta(days=age_limit_days) if age_limit_days else None
                ),
                "FORCE_LAST_UPDATED": scraper_event.forceLastUpdated,
            },
            "OPENSEARCH": {
                "INDEX": index,
                "MAPPING": {"dynamic": "strict", "properties": decision_raw_mapping},
                "BATCH_SIZE": int_env("OPENSEARCH_BATCH_SIZE", 15),
                "CREDENTIALS_SECRET": os.getenv("OPENSEARCH_CREDENTIALS_SECRET"),
            },
            "EXTENSIONS": {
                "scrapy.extensions.closespider.CloseSpider": 100,
            },
            "CLOSESPIDER_ITEMCOUNT": scraper_event.limitItems,
            "CLOSESPIDER_ERRORCOUNT": 5,
            **log_settings,
        }
        crawler = Crawler(UpdatedOutcomesSpider, settings)
        crawler.signals.connect(add_ref, signal=signals.item_scraped)
        runner = CrawlerRunner(settings)
        return runner.crawl(crawler)

    run_spider()
    logging.info(f"Scraped {len(references)} decisions")
    return references
