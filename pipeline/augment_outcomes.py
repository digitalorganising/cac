import bytewax.operators as op
from bytewax.dataflow import Dataflow
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .extractors import get_extracted_data
from .services.opensearch_connectors import OpensearchSink, OpensearchSource


class OutcomeSink(OpensearchSink):
    def doc(self, item):
        document_type = item.pop("document_type")
        extracted_data = item.pop("extracted_data")
        content = item.pop("content", None)
        return {
            **item,
            "documents": {document_type: content},
            "extracted_data": {document_type: extracted_data},
        }

    def id(self, item):
        return item["reference"]


def flat_map_outcome(outcome):
    outcome_doc = outcome["_source"]
    documents = outcome_doc.pop("documents", {})
    for document_type, content in documents.items():
        yield {**outcome_doc, "document_type": document_type, "content": content}


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def augment_doc(doc):
    return {**doc, "extracted_data": get_extracted_data(doc)}


outcomes_source = OpensearchSource(
    cluster_host="http://127.0.0.1",
    cluster_user=None,
    cluster_pass=None,
    index="outcomes-raw",
    page_size=10,
)
opensearch_sink = OutcomeSink(
    cluster_host="http://127.0.0.1",
    cluster_user=None,
    cluster_pass=None,
    index="outcomes-transformed",
)


flow = Dataflow("outcome_augmentation")
stream = op.input("outcome_docs", flow, outcomes_source)
split_docs = op.flat_map("split_docs", stream, flat_map_outcome)
augmented_docs = op.map("augmented_docs", split_docs, augment_doc)
op.output("write", augmented_docs, opensearch_sink)
