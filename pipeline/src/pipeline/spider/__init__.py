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
    def __init__(self, index, add_reference):
        self.index = index
        self.add_reference = add_reference
        self.ids_set = set()

    @classmethod
    def from_crawler(cls, crawler):
        opensearch_settings = crawler.settings.get("OPENSEARCH")
        add_reference = crawler.settings.get("ADD_REFERENCE")
        return cls(
            index=opensearch_settings.get("INDEX"),
            add_reference=add_reference,
        )

    def process_item(self, item, spider):
        id = item["reference"]
        if id not in self.ids_set:
            self.ids_set.add(id)
            self.add_reference(
                {
                    "_id": id,
                    "_index": self.index,
                }
            )
