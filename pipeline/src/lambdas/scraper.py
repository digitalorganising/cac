import os
import logging
from scrapy.crawler import CrawlerProcess

from pipeline.spider import QuietDroppedLogFormatter, ReferenceSQSPipeline
from pipeline.spider.all_outcomes import AllOutcomesSpider
from pipeline.spider.cac_outcome_spider import CacOutcomeOpensearchPipeline

# https://github.com/scrapy/scrapy/issues/3587#issuecomment-456842238
root_logger = logging.getLogger()
for log_handler in root_logger.handlers:
    root_logger.removeHandler(log_handler)


def handler(event, context):
    index_suffix = event.get("indexSuffix")
    index = f"outcomes-raw-{index_suffix}" if index_suffix else "outcomes-raw"
    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "INFO",
            "LOG_FORMATTER": QuietDroppedLogFormatter,
            "ITEM_PIPELINES": {
                CacOutcomeOpensearchPipeline: 100,
                ReferenceSQSPipeline: 200,
            },
            "CONCURRENT_ITEMS": 10,
            "OPENSEARCH": {
                "INDEX": index,
                "MAPPING_PATH": "./index_mappings/outcomes_raw.json",
            },
            "SQS": {
                "QUEUE_URL": os.getenv("SQS_QUEUE_URL"),
                "GROUP_ID": "crawled-outcomes",
                "INDEX": index,
            },
        }
    )
    process.crawl(AllOutcomesSpider)
    process.start()
