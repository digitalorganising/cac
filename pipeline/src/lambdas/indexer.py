from pipeline.transforms import transform_for_index

from . import map_docs, RefsEvent, lambda_friendly_run_async


async def transform(doc):
    return transform_for_index(doc)


async def process_batch(refs):
    return await map_docs(
        refs,
        transform,
        dest_namespace="outcomes-indexed",
        dest_mapping="./index_mappings/outcomes_indexed.json",
    )


def handler(event, context):
    indexer_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(indexer_event.refs))
