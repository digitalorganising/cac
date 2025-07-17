import logging
import os
from scrapy.exceptions import DropItem
from scrapy.logformatter import LogFormatter


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


class ReferencePipeline:
    def __init__(self, index):
        self.index = index

    @classmethod
    def from_crawler(cls, crawler):
        opensearch_settings = crawler.settings.get("OPENSEARCH")
        return cls(
            index=opensearch_settings.get("INDEX"),
        )

    def process_item(self, item, spider):
        return {
            "_id": item["reference"],
            "_index": self.index,
        }
