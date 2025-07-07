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
    def message(self, item):
        return {"reference": item["reference"]}
