import asyncio
from opensearchpy import helpers

from pipeline.transforms.augmentation import augment_doc
from pipeline.transforms.withdrawals import merge_withdrawal

from . import get_docs, client, RefsEvent, lambda_friendly_run_async


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

    saved_refs = []
    async for update_doc, doc in get_docs(
        refs,
        destination_index_namespace="outcomes-augmented",
        destination_index_mapping="./index_mappings/outcomes_augmented.json",
    ):
        augmented_doc = await augment_doc(doc)
        if augmented_doc["reference"] in withdrawals:
            withdrawal = withdrawals[augmented_doc["reference"]]
            augmented_doc = merge_withdrawal(withdrawal, augmented_doc)
        saved_ref = await update_doc(augmented_doc)
        saved_refs.append(saved_ref.model_dump(by_alias=True))
    return saved_refs


def handler(event, context):
    augmenter_event = RefsEvent.model_validate(event)
    return lambda_friendly_run_async(process_batch(augmenter_event.refs))
