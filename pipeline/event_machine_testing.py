from opensearchpy import OpenSearch
from transforms.events import events_from_outcome

opensearch = OpenSearch(hosts=["127.0.0.1:"])
doc_id = "TUR1/1394(2024)"

doc = opensearch.get(index="outcomes-augmented", id=doc_id)

efd = events_from_outcome(doc["_source"])
print(efd.dump_events())
print(efd.labelled_state())

