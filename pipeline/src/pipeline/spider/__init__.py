import logging
import os
from scrapy.exceptions import DropItem
from scrapy.logformatter import LogFormatter
from ..services.sqs_pipeline import SQSPipeline


class QuietDroppedLogFormatter(LogFormatter):
    def dropped(self, item, exception, response, spider):
        if isinstance(exception, DropItem) and str(exception) == "skip":
            return {
                "level": logging.DEBUG,
                "msg": "Dropped: %(exception)s" + os.linesep + "%(item)s",
                "args": {
                    "exception": exception,
                    "item": item,
                },
            }
        else:
            return super().dropped(item, exception, response, spider)


class ReferenceSQSPipeline(SQSPipeline):
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("SQS")
        return cls(
            index=settings.get("INDEX"),
            queue_url=settings.get("QUEUE_URL"),
            group_id=settings.get("GROUP_ID"),
        )

    def message(self, item):
        return {
            "_id": item["reference"],
            "_index": self.index,
        }
