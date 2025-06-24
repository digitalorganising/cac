from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess

from ..document_classifier import DocumentType
from ..services.opensearch_pipeline import OpensearchPipeline
from .cac_outcome_spider import CacOutcomeSpider


class CacOutcomeOpensearchPipeline(OpensearchPipeline):
    def skip_item(self, item):
        match ItemAdapter(item)["document_type"]:
            case DocumentType.derecognition_decision:
                return "Skipping a derecognition decision"
            case _:
                False

    def id(self, item):
        return item["reference"]

    def doc(self, item):
        data = ItemAdapter(item).asdict()
        document_content = data.pop("document_content", None)
        document_url = data.pop("document_url", None)
        document_fingerprint = data.pop("document_fingerprint", None)
        document_type = data.pop("document_type")
        return {
            **data,
            "documents": {document_type: document_content},
            "document_urls": {document_type: document_url},
            "document_fingerprints": {document_type: document_fingerprint},
        }


def scrape():
    process = CrawlerProcess(
        settings={
            "LOG_LEVEL": "INFO",
            "ITEM_PIPELINES": {CacOutcomeOpensearchPipeline: 100},
            "CONCURRENT_ITEMS": 10,
            "OPENSEARCH": {
                "INDEX": "outcomes-raw-20250624",
                "MAPPING_PATH": "./pipeline/index_mappings/outcomes_raw.json",
            },
        }
    )
    process.crawl(CacOutcomeSpider)
    process.start()


if __name__ == "__main__":
    scrape()
