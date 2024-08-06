import bytewax.operators as op
from bytewax.dataflow import Dataflow

from .services.opensearch_connectors import OpensearchSink, OpensearchSource


class OutcomeSink(OpensearchSink):
    def doc(self, item):
        return {"titularity": item["_source"]["outcome_title"]}

    def id(self, item):
        return item["_id"]


flow = Dataflow("outcome_augmentation")
stream = op.input(
    "docs",
    flow,
    OpensearchSource(
        cluster_host="http://127.0.0.1",
        cluster_user=None,
        cluster_pass=None,
        index="outcomes-raw",
    ),
)
op.output(
    "write",
    stream,
    OutcomeSink(
        cluster_host="http://127.0.0.1",
        cluster_user=None,
        cluster_pass=None,
        index="outcomes-transformed",
    ),
)
