from pipeline.decisions_to_outcomes import merge_decisions_to_outcome
from pipeline.services.opensearch_utils import get_mapping_from_path
from pipeline.transforms import transform_for_index
from pipeline.transforms.events import InvalidEventError

from . import RefEvent, client, DocumentRef, lambda_friendly_run_async, map_doc


def transform_if_possible(outcome):
    try:
        return transform_for_index(outcome)
    except InvalidEventError as e:
        print(f"Invalid event error: {e}")
        return None


def reference_from_id(id):
    # rpartition rather than split in case the ID is a URI with a scheme...
    return id.rpartition(":")[0]


async def process_ref(ref: DocumentRef):
    outcome_reference = reference_from_id(ref.id)
    outcome = await merge_decisions_to_outcome(
        client,
        index=ref.index,
        non_pipeline_indices={"application-withdrawals"},
        reference=outcome_reference,
    )
    if outcome is None:
        raise ValueError(
            f"No merged outcome for reference {outcome_reference!r} (ref {ref.id!r})"
        )

    write_ref = DocumentRef(
        _id=outcome.id,
        _index=ref.index,
        passthrough=False,
    )
    return await map_doc(
        outcome,
        write_ref,
        transform=transform_if_possible,
        dest_namespace="outcomes-indexed",
        dest_mapping=get_mapping_from_path("./index_mappings/outcomes_indexed.json"),
    )


def handler(event, context):
    indexer_event = RefEvent.model_validate(event)
    return lambda_friendly_run_async(process_ref(indexer_event.ref))
