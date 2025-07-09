import os
import logging
from typing import Optional

import crochet
from pydantic import BaseModel
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor
from scrapy.utils.log import configure_logging

from pipeline.spider import QuietDroppedLogFormatter, ReferenceSQSPipeline
from pipeline.spider.all_outcomes import AllOutcomesSpider
from pipeline.spider.cac_outcome_spider import CacOutcomeOpensearchPipeline

# https://github.com/scrapy/scrapy/issues/3587#issuecomment-456842238
root_logger = logging.getLogger()
for log_handler in root_logger.handlers:
    root_logger.removeHandler(log_handler)

# Install the asyncio reactor for Lambda compatibility
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
crochet.setup()

configure_logging(
    {
        "LOG_LEVEL": "INFO",
        "LOG_FORMATTER": QuietDroppedLogFormatter,
    }
)


class ScraperEvent(BaseModel):
    indexSuffix: Optional[str] = None
    limitItems: Optional[int] = None


def handler(event, context):
    scraper_event = ScraperEvent.model_validate(event)
    index_suffix = scraper_event.indexSuffix
    index = f"outcomes-raw-{index_suffix}" if index_suffix else "outcomes-raw"
    settings = {
        "ITEM_PIPELINES": {
            CacOutcomeOpensearchPipeline: 100,
            ReferenceSQSPipeline: 200,
        },
        "CONCURRENT_ITEMS": 5,
        "OPENSEARCH": {
            "INDEX": index,
            "MAPPING_PATH": "./index_mappings/outcomes_raw.json",
        },
        "SQS": {
            "QUEUE_URL": os.getenv("SQS_QUEUE_URL"),
            "GROUP_ID": "crawled-outcomes",
            "INDEX": index,
        },
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 100,
        },
        "CLOSESPIDER_ITEMCOUNT": scraper_event.limitItems,
    }

    @crochet.wait_for(timeout=60 * 60)  # More than the maximum possible lambda timeout
    def run_spider():
        runner = CrawlerRunner(settings)
        return runner.crawl(AllOutcomesSpider)

    return run_spider()
