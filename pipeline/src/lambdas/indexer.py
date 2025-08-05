from pipeline.transforms import transform_for_index

from pipeline.decisions_to_outcomes import merge_decisions_to_outcomes
from pipeline.services.opensearch_utils import get_mapping_from_path
from . import map_docs, RefsEvent, lambda_friendly_run_async, client, DocumentRef


async def async_transform(doc):
    return transform_for_index(doc)


def reference_from_id(id):
    return id.split(":")[0]


async def outcomes_from_refs(client, *, refs, additional_indices={}):
    references = set(reference_from_id(ref.id) for ref in refs)
    indices = set(ref.index for ref in refs) | additional_indices
    async for outcome, index in merge_decisions_to_outcomes(
        client,
        indices=indices,
        non_pipeline_indices=additional_indices,
        references=list(references),
    ):
        ref = DocumentRef(
            _id=outcome.id,
            _index=index,
        )
        yield outcome, ref


async def process_batch(refs):
    outcomes = outcomes_from_refs(
        client, refs=refs, additional_indices={"application-withdrawals"}
    )
    return await map_docs(
        outcomes,
        transform=async_transform,
        dest_namespace="outcomes-indexed",
        dest_mapping=get_mapping_from_path("./index_mappings/outcomes_indexed.json"),
    )


def handler(event, context):
    indexer_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(indexer_event.refs))
