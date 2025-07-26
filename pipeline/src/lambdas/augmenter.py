import asyncio
from opensearchpy import helpers

from pipeline.transforms.augmentation import augment_doc
from pipeline.transforms.withdrawals import merge_withdrawal

from . import map_docs, client, RefsEvent, lambda_friendly_run_async


# Small enough that I don't mind storing this in memory
async def get_withdrawals(withdrawals_index):
    w = {}
    async for hit in helpers.async_scan(client, index=withdrawals_index):
        src = hit["_source"]
        w[hit["_id"]] = {
            "application_withdrawn": src["application_withdrawn"],
            "application_received": src["application_received"],
        }
    print(f"Successfully loaded {len(w)} withdrawals")
    return w


withdrawals = None


async def process_batch(refs):
    global withdrawals
    if withdrawals is None:
        withdrawals = await get_withdrawals("application-withdrawals")

    async def augment(doc):
        augmented_doc = await augment_doc(doc)
        reference = augmented_doc["reference"]
        if reference in withdrawals:
            withdrawal = withdrawals[reference]
            # TODO work this out
            augmented_doc = merge_withdrawal(withdrawal, augmented_doc)
        return augmented_doc

    return await map_docs(
        refs,
        augment,
        dest_namespace="outcomes-augmented",
        dest_mapping="./index_mappings/outcomes_augmented.json",
    )


def handler(event, context):
    augmenter_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(augmenter_event.refs))
