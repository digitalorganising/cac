import logging
import os
from datetime import timedelta
from typing import Optional

import crochet
from pydantic import BaseModel
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor
from scrapy.utils.log import configure_logging

from pipeline.spider import QuietDroppedLogFormatter, ReferencePipeline
from pipeline.spider.updated_outcomes import UpdatedOutcomesSpider
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
    forceLastUpdated: Optional[str] = None


def handler(event, context):
    scraper_event = ScraperEvent.model_validate(event)
    index_suffix = scraper_event.indexSuffix
    index = f"outcomes-raw-{index_suffix}" if index_suffix else "outcomes-raw"

    references = []

    def add_ref(ref):
        references.append(ref)

    @crochet.wait_for(timeout=60 * 60)  # More than the maximum possible lambda timeout
    def run_spider():
        age_limit_days = os.getenv("UNTERMINATED_OUTCOMES_AGE_LIMIT_DAYS")
        settings = {
            "ITEM_PIPELINES": {
                CacOutcomeOpensearchPipeline: 100,
                ReferencePipeline: 200,
            },
            "OUTCOMES": {
                "ADD_REFERENCE": add_ref,
                "API_BASE": os.getenv("API_BASE"),
                "START_DATE": "2014-01-01",
                "UNTERMINATED_OUTCOMES_AGE_LIMIT": (
                    timedelta(days=int(age_limit_days)) if age_limit_days else None
                ),
                "FORCE_LAST_UPDATED": scraper_event.forceLastUpdated,
            },
            "OPENSEARCH": {
                "INDEX": index,
                "MAPPING_PATH": "./index_mappings/outcomes_raw.json",
                "BATCH_SIZE": int(os.getenv("OPENSEARCH_BATCH_SIZE", 15)),
            },
            "EXTENSIONS": {
                "scrapy.extensions.closespider.CloseSpider": 100,
            },
            "CLOSESPIDER_ITEMCOUNT": scraper_event.limitItems,
            "CLOSESPIDER_ERRORCOUNT": 5,
            **log_settings,
        }
        runner = CrawlerRunner(settings)
        return runner.crawl(UpdatedOutcomesSpider)

    run_spider()
    logging.info(f"Scraped {len(references)} outcomes")
    return references
