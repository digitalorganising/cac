import asyncio
from abc import ABC, abstractmethod
import os

import scrapy
from opensearchpy import helpers
from twisted.internet.defer import Deferred

from .opensearch_utils import get_auth, create_client, ensure_index_mapping


def deferred(coroutine):
    loop = asyncio.get_event_loop()
    return Deferred.fromFuture(loop.create_task(coroutine))


class OpensearchPipeline(ABC):
    ingest_queue = asyncio.Queue()
    worker_tasks = set()

    def skip_item(self, item):
        return False

    @abstractmethod
    def doc(self, item):
        pass

    @abstractmethod
    def id(self, item):
        pass

    def __init__(
        self,
        cluster_host,
        auth,
        index,
        batch_size=5,
        concurrency=1,
        mapping_path=None,
    ):
        self.cluster_host = cluster_host
        self.auth = auth
        self.index = index
        self.batch_size = batch_size
        self.concurrency = concurrency
        self.mapping_path = mapping_path

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("OPENSEARCH")
        auth = get_auth(user=settings.get("USER"), password=settings.get("PASS"))
        return cls(
            cluster_host=settings.get("HOST", os.getenv("OPENSEARCH_ENDPOINT")),
            index=settings.get("INDEX"),
            auth=auth,
            mapping_path=settings.get("MAPPING_PATH"),
        )

    def open_spider(self, spider):
        self.client = create_client(
            cluster_host=self.cluster_host,
            auth=self.auth,
            async_client=True,
        )

        async def setup():
            await self.client.ping()
            await ensure_index_mapping(
                client=self.client,
                index=self.index,
                mapping_path=self.mapping_path,
                logger=spider.logger,
            )
            for _ in range(self.concurrency):
                self.start_worker(spider)

        return deferred(setup())

    def close_spider(self, spider):
        async def shutdown():
            spider.logger.info(
                f"Shutting down after processing {self.ingest_queue.qsize()} "
                f"items remaining on the queue"
            )
            await self.ingest_queue.join()
            for task in self.worker_tasks:
                task.cancel()
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            await self.client.close()

        return deferred(shutdown())

    def start_worker(self, spider):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.index_worker())
        task.add_done_callback(self.worker_done_handler(spider))
        self.worker_tasks.add(task)

    def worker_done_handler(self, spider):
        def handle_done(task):
            self.worker_tasks.remove(task)

            try:
                exc = task.exception()
                if exc:
                    spider.logger.error(exc.exception)
                    self.start_worker(spider)
            except (Exception, asyncio.exceptions.CancelledError):
                pass

        return handle_done

    async def index_worker(self):
        while True:
            items = []
            while len(items) < self.batch_size:
                item = await self.ingest_queue.get()
                items.append(item)
                if self.ingest_queue.empty():
                    break

            if items:
                ingest_actions = [
                    {
                        "_op_type": "update",
                        "_index": self.index,
                        "_id": self.id(item),
                        "doc": self.doc(item),
                        "doc_as_upsert": True,
                        "retry_on_conflict": 3,
                    }
                    for item in items
                ]
                try:
                    await helpers.async_bulk(self.client, ingest_actions)
                finally:
                    for _ in items:
                        self.ingest_queue.task_done()

    async def process_item(self, item, spider):
        skip_reason = self.skip_item(item)
        if skip_reason:
            raise scrapy.exceptions.DropItem(skip_reason)
        await self.ingest_queue.put(item)
        return item
