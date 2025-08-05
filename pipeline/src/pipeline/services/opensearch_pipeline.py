import asyncio
from abc import ABC, abstractmethod
import os

import scrapy
from twisted.internet.defer import Deferred
from async_batcher.batcher import AsyncBatcher
from opensearchpy import helpers

from .opensearch_utils import get_auth, create_client, ensure_index_mapping


def deferred(coroutine):
    loop = asyncio.get_event_loop()
    return Deferred.fromFuture(loop.create_task(coroutine))


class OpensearchAsyncBatcher(AsyncBatcher):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    def handle_result(self, ok, result):
        if not ok:
            return Exception("Failed to index item", result)
        if result["update"]["result"] == "noop":
            return scrapy.exceptions.DropItem(
                "duplicate - cluster reported noop update"
            )
        return None

    async def process_batch(self, batch):
        if not self.client:
            raise Exception("Client not initialized")
        results_stream = helpers.async_streaming_bulk(client=self.client, actions=batch)
        return [self.handle_result(ok, result) async for ok, result in results_stream]


class OpensearchPipeline(ABC):
    async def skip_item(self, item):
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
        mapping=None,
        batch_size=15,
    ):
        self.cluster_host = cluster_host
        self.auth = auth
        self.index = index
        self.mapping = mapping
        self.batch_size = batch_size

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("OPENSEARCH")
        auth = get_auth(
            user=settings.get("USER"),
            password=settings.get("PASS"),
            credentials_secret=settings.get("CREDENTIALS_SECRET"),
        )
        return cls(
            cluster_host=settings.get("HOST", os.getenv("OPENSEARCH_ENDPOINT")),
            index=settings.get("INDEX"),
            auth=auth,
            mapping=settings.get("MAPPING"),
            batch_size=settings.get("BATCH_SIZE"),
        )

    def open_spider(self, spider):
        async def _open_spider():
            self.client = create_client(
                cluster_host=self.cluster_host,
                auth=self.auth,
                async_client=True,
            )
            await self.client.ping()
            await ensure_index_mapping(
                client=self.client,
                index=self.index,
                mapping=self.mapping,
            )

            self.batcher = OpensearchAsyncBatcher(
                client=self.client,
                max_batch_size=self.batch_size,
                max_queue_size=2 * self.batch_size,
                max_queue_time=1,
                concurrency=1,
            )

        return deferred(_open_spider())

    def close_spider(self, spider):
        async def _close_spider():
            await self.batcher.stop(force=False)
            await self.client.close()

        return deferred(_close_spider())

    def action(self, item):
        return {
            "_op_type": "update",
            "_index": self.index,
            "_id": self.id(item),
            "doc": self.doc(item),
            "doc_as_upsert": True,
            "retry_on_conflict": 3,
        }

    async def process_item(self, item, spider):
        if await self.skip_item(item):
            raise scrapy.exceptions.DropItem("skip")

        await self.batcher.process(self.action(item))
        return item
