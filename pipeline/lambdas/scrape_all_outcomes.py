from scrapy.crawler import CrawlerProcess

from pipeline.spider import QuietDroppedLogFormatter
from pipeline.spider.all_outcomes import AllOutcomesSpider
from pipeline.spider.cac_outcome_spider import CacOutcomeOpensearchPipeline


def handler(event, context):
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
