import asyncio
from abc import ABC, abstractmethod

from opensearchpy import AsyncOpenSearch, helpers
from twisted.internet.defer import Deferred


def deferred(coroutine):
    loop = asyncio.get_event_loop()
    return Deferred.fromFuture(loop.create_task(coroutine))


class OpensearchPipeline(ABC):
    ingest_queue = asyncio.Queue()
    worker_tasks = set()

    @abstractmethod
    def doc(self, item):
        pass

    @abstractmethod
    def id(self, item):
        pass

    def __init__(
        self,
        cluster_host,
        cluster_user,
        cluster_pass,
        index,
        batch_size=10,
        concurrency=3,
    ):
        self.cluster_host = cluster_host
        self.cluster_user = cluster_user
        self.cluster_pass = cluster_pass
        self.index = index
        self.batch_size = batch_size
        self.concurrency = concurrency

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("OPENSEARCH")
        return cls(
            cluster_host=settings.get("HOST"),
            index=settings.get("INDEX"),
            cluster_user=settings.get("USER", None),
            cluster_pass=settings.get("PASS", None),
        )

    def open_spider(self, spider):
        http_auth = (self.cluster_user, self.cluster_pass)
        self.client = AsyncOpenSearch(
            hosts=[self.cluster_host],
            use_ssl=("https" in self.cluster_host),
            http_auth=http_auth if all(http_auth) else None,
            http_compress=True,
        )
        for _ in range(self.concurrency):
            self.start_worker(spider)
        return deferred(self.client.ping())

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
            except Exception:
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
        await self.ingest_queue.put(item)
        return item
