import bytewax.operators as op
from bytewax.dataflow import Dataflow
from tenacity import retry, stop_after_attempt, wait_random_exponential
import os

from .extractors import get_extracted_data
from .services.opensearch_connectors import OpensearchSink, OpensearchSource

fast_forward = bool(os.getenv("FAST_FORWARD"))


class OutcomeSink(OpensearchSink):
    def doc(self, item):
        document_type = item.pop("document_type")
        content = item.pop("content", None)
        url = item.pop("document_url", None)
        if fast_forward:
            return {
                **item,
                "documents": {document_type: content},
                "document_urls": {document_type: url},
            }

        extracted_data = item.pop("extracted_data")
        return {
            **item,
            "documents": {document_type: content},
            "document_urls": {document_type: url},
            "extracted_data": {document_type: extracted_data},
        }

    def id(self, item):
        return item["reference"]


def flat_map_outcome(outcome):
    outcome_doc = outcome["_source"]
    documents = outcome_doc.pop("documents", {})
    document_urls = outcome_doc.pop("document_urls", {})
    for document_type, content in documents.items():
        yield {
            **outcome_doc,
            "document_type": document_type,
            "content": content,
            "document_url": document_urls.get(document_type),
        }


@retry(
    wait=wait_random_exponential(min=1, max=90),
    stop=stop_after_attempt(7),
    reraise=True,
)
def augment_doc(doc):
    return {**doc, "extracted_data": get_extracted_data(doc)}


outcomes_source = OpensearchSource(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-raw-2025",
    page_size=5,
    query={"term": {"reference": "TUR1/1194(2020)"}},
)
opensearch_sink = OutcomeSink(
    cluster_host=os.getenv("OPENSEARCH_ENDPOINT"),
    index="outcomes-augmented",
    mapping_path="./pipeline/index_mappings/outcomes_augmented.json",
)


flow = Dataflow("outcome_augmentation")
stream = op.input("outcome_docs", flow, outcomes_source)
split_docs = op.flat_map("split_docs", stream, flat_map_outcome)

if not fast_forward:
    augmented_docs = op.map("augmented_docs", split_docs, augment_doc)
    op.output("write", augmented_docs, opensearch_sink)
else:
    op.output("write", split_docs, opensearch_sink)
