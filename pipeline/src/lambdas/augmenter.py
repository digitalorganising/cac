import asyncio
from opensearchpy import helpers

from pipeline.transforms.augmentation import augment_doc
from pipeline.transforms.withdrawals import merge_withdrawal

from . import get_docs, client, RefsEvent


# Small enough that I don't mind storing this in memory
async def get_withdrawals(withdrawals_index):
    w = {}
    async for hit in helpers.async_scan(client, index=withdrawals_index):
        src = hit["_source"]
        w[hit["_id"]] = {
            "application_withdrawn": src["application_withdrawn"],
            "application_received": src["application_received"],
        }
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
    loop = asyncio.get_event_loop()
    if loop.is_closed():  # I don't know why
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(process_batch(augmenter_event.refs))
