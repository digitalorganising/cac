from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, AsyncIterator, Iterable, List, Optional

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition, batch_async
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from opensearchpy import exceptions, helpers

from .opensearch_utils import get_auth, create_client, ensure_index_mapping


class OpensearchStatefulSourcePartition(
    StatefulSourcePartition[Any, Optional[List[str]]]
):
    def __init__(
        self,
        cluster_host,
        index,
        page_size,
        query,
        sort,
        search_after,
        cluster_user=None,
        cluster_pass=None,
    ):
        self.search_after = search_after
        async_generator = self._opensearch_source(
            cluster_host=cluster_host,
            cluster_user=cluster_user,
            cluster_pass=cluster_pass,
            index=index,
            page_size=page_size,
            query=query,
            sort=sort,
        )

        self._batcher = batch_async(
            async_generator, timedelta(milliseconds=500), page_size
        )

    def next_batch(self) -> Iterable[Any]:
        return next(self._batcher)

    def snapshot(self):
        return self.search_after

    async def _opensearch_source(
        self,
        cluster_host,
        index,
        page_size,
        query,
        sort,
        cluster_user=None,
        cluster_pass=None,
    ) -> AsyncIterator[Any]:
        auth = get_auth(user=cluster_user, password=cluster_pass)
        client = create_client(cluster_host=cluster_host, auth=auth, async_client=True)

        async def do_search():
            try:
                search_body = {
                    "query": query,
                    "sort": sort,
                    "size": page_size,
                }
                if self.search_after:
                    search_body["search_after"] = self.search_after
                res = await client.search(index=index, body=search_body)
                return res.get("hits", {}).get("hits", [])
            except exceptions.OpenSearchException as e:
                print(e)
                raise e

        hits = await do_search()
        try:
            while hits:
                for hit in hits:
                    yield hit
                    self.search_after = hit.get("sort")

                hits = await do_search()
        finally:
            await client.close()


class OpensearchSource(FixedPartitionedSource[Any, List[str]]):
    def __init__(
        self,
        cluster_host,
        index,
        page_size=25,
        query={"match_all": {}},
        sort=[{"_id": "asc"}],
        cluster_user=None,
        cluster_pass=None,
    ):
        self.cluster_host = cluster_host
        self.cluster_user = cluster_user
        self.cluster_pass = cluster_pass
        self.index = index
        self.page_size = page_size
        self.query = query
        self.sort = sort

    def list_parts(self) -> List[str]:
        return [self.index]

    def build_part(
        self,
        step_id: str,
        for_part: str,
        resume_state: Optional[List[str]],
    ) -> StatefulSourcePartition[Any, List[str]]:
        return OpensearchStatefulSourcePartition(
            cluster_host=self.cluster_host,
            cluster_user=self.cluster_user,
            cluster_pass=self.cluster_pass,
            index=self.index,
            page_size=self.page_size,
            query=self.query,
            sort=self.sort,
            search_after=resume_state,
        )


class OpensearchStatelessSinkPartition(StatelessSinkPartition[Any]):
    def __init__(
        self,
        cluster_host,
        index,
        get_doc,
        get_id,
        cluster_user=None,
        cluster_pass=None,
    ):
        self.index = index
        self.get_doc = get_doc
        self.get_id = get_id

        auth = get_auth(user=cluster_user, password=cluster_pass)
        self._client = create_client(
            cluster_host=cluster_host, auth=auth, async_client=False
        )

    def to_action(self, item):
        return {
            "_op_type": "update",
            "_index": self.index,
            "_id": self.get_id(item),
            "doc": self.get_doc(item),
            "doc_as_upsert": True,
            "retry_on_conflict": 3,
        }

    def write_batch(self, items: List[Any]) -> None:
        ingest_actions = [self.to_action(item) for item in items]
        try:
            helpers.bulk(self._client, ingest_actions)
        except exceptions.OpenSearchException as e:
            print(e)
            raise e

    def close(self):
        self._client.close()


class OpensearchSink(DynamicSink[Any], ABC):
    def __init__(
        self,
        cluster_host,
        index,
        mapping_path=None,
        cluster_user=None,
        cluster_pass=None,
    ):
        self.cluster_host = cluster_host
        self.cluster_user = cluster_user
        self.cluster_pass = cluster_pass
        self.index = index
        self.mapping_path = mapping_path

    def doc(self, item) -> Any:
        return item

    @abstractmethod
    def id(self, item) -> str:
        pass

    async def _ensure_mapping(self):
        """Ensure the index exists with the correct mapping before starting ingestion."""
        auth = get_auth(user=self.cluster_user, password=self.cluster_pass)
        client = create_client(
            cluster_host=self.cluster_host, auth=auth, async_client=True
        )
        try:
            await ensure_index_mapping(
                client=client, index=self.index, mapping_path=self.mapping_path
            )
        finally:
            await client.close()

    def build(self, step_id: str, worker_index: int, worker_count: int):
        # Ensure mapping is set up before creating the sink partition
        import asyncio

        asyncio.run(self._ensure_mapping())

        return OpensearchStatelessSinkPartition(
            cluster_host=self.cluster_host,
            cluster_user=self.cluster_user,
            cluster_pass=self.cluster_pass,
            index=self.index,
            get_doc=self.doc,
            get_id=self.id,
        )
