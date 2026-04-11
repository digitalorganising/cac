from typing import Optional
from pipeline.decisions_to_outcomes import merge_decisions_to_outcome
from pipeline.services.opensearch_utils import get_mapping_from_path
from pipeline.transforms import transform_for_index
from pipeline.transforms.events import InvalidEventError

from . import RefEvent, client, DocumentRef, lambda_friendly_run_async, map_doc


class CompanyRefEvent(RefEvent):
    company_ref: Optional[DocumentRef] = None


def transform_if_possible(outcome):
    try:
        return transform_for_index(outcome)
    except InvalidEventError as e:
        print(f"Invalid event error: {e}")
        return None


def reference_from_id(id):
    # rpartition rather than split in case the ID is a URI with a scheme...
    return id.rpartition(":")[0]


async def process_event(event: CompanyRefEvent):
    decision_ref = event.ref
    outcome_reference = reference_from_id(decision_ref.id)
    outcome = await merge_decisions_to_outcome(
        client,
        index=decision_ref.index,
        non_pipeline_indices={"application-withdrawals"},
        reference=outcome_reference,
        company_ref=event.company_ref,
    )
    if outcome is None:
        print(
            f"No merged outcome for reference {outcome_reference!r} (ref {decision_ref.id!r})"
        )
        return None

    write_ref = DocumentRef(
        _id=outcome.id,
        _index=decision_ref.index,
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
    indexer_event = CompanyRefEvent.model_validate(event)
    return lambda_friendly_run_async(process_event(indexer_event))
