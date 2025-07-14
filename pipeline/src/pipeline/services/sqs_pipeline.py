import boto3
import json
from abc import ABC, abstractmethod

class SQSPipeline(ABC):
    @abstractmethod
    def message(self, item):
        pass

    def __init__(self, queue_url: str, group_id: str):
        self.queue_url = queue_url
        self.group_id = group_id

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("SQS")
        return cls(
            queue_url=settings.get("QUEUE_URL"),
            group_id=settings.get("GROUP_ID"),
        )

    def process_item(self, item, spider):
        msg = self.message(item)
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(msg),
            MessageGroupId=self.group_id,
        )

    def open_spider(self, spider):
        session = boto3.Session()
        self.client = session.client("sqs")

    def close_spider(self, spider):
        pass
