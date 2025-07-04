import asyncio
from abc import ABC, abstractmethod
import os

import scrapy
from twisted.internet.defer import Deferred

from .opensearch_utils import get_auth, create_client, ensure_index_mapping


def deferred(coroutine):
    loop = asyncio.get_event_loop()
    return Deferred.fromFuture(loop.create_task(coroutine))


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
        mapping_path=None,
    ):
        self.cluster_host = cluster_host
        self.auth = auth
        self.index = index
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
            )

        return deferred(setup())

    def close_spider(self, spider):
        async def shutdown():
            await self.client.close()

        return deferred(shutdown())

    async def process_item(self, item, spider):
        if await self.skip_item(item):
            raise scrapy.exceptions.DropItem("skip")
        await self.client.update(
            index=self.index,
            id=self.id(item),
            body={
                "doc": self.doc(item),
                "doc_as_upsert": True,
            },
            retry_on_conflict=3,
        )
        return item
