import logging
import os
from scrapy.exceptions import DropItem
from scrapy.logformatter import LogFormatter


class QuietDroppedLogFormatter(LogFormatter):
    def should_suppress(self, exception):
        if isinstance(exception, DropItem):
            if str(exception) == "skip":
                return True
            if "duplicate" in str(exception):
                return True
        return False

    def dropped(self, item, exception, response, spider):
        if self.should_suppress(exception):
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
