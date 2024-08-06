import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow

from .services.opensearch_connectors import OpensearchFixedPartionedSource

flow = Dataflow("outcome_augmentation")
stream = op.input(
    "docs",
    flow,
    OpensearchFixedPartionedSource(
        cluster_host="http://127.0.0.1",
        cluster_user=None,
        cluster_pass=None,
        index="outcomes-raw",
    ),
)
count = op.count_final("count", stream, lambda doc: "any")
op.output("print", count, StdOutSink())
