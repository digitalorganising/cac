import asyncio

from itemadapter import ItemAdapter
from opensearchpy import AsyncOpenSearch
from twisted.internet.defer import Deferred


def deferred(coroutine):
    loop = asyncio.get_event_loop()
    return Deferred.fromFuture(loop.create_task(coroutine))


class OpensearchPipeline:
    def __init__(self, cluster_host, cluster_user, cluster_pass, index):
        self.cluster_host = cluster_host
        self.cluster_user = cluster_user
        self.cluster_pass = cluster_pass
        self.index = index

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("OPENSEARCH")
        return cls(
            cluster_host=settings.get("HOST"),
            cluster_user=settings.get("USER", None),
            cluster_pass=settings.get("PASS", None),
            index=settings.get("INDEX", "outcomes"),
        )

    def open_spider(self, spider):
        http_auth = (self.cluster_user, self.cluster_pass)
        self.client = AsyncOpenSearch(
            hosts=[self.cluster_host],
            use_ssl=("https" in self.cluster_host),
            http_auth=http_auth if all(http_auth) else None,
            http_compress=True,
        )
        return deferred(self.client.ping())

    def close_spider(self, spider):
        return deferred(self.client.close())

    async def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        doc_id = f"{data['reference']}_{data['document_type'] or 0}"
        await self.client.index(index=self.index, body=data, id=doc_id)
        return item
