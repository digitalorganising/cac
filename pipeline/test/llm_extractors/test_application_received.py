from pipeline.baml_client import b


async def test_application_received():
    statement = (
        "This application was received on 24 June 2024,"
        "and no decisions have yet been issued."
    )
    result = await b.ExtractApplicationReceived(statement)

    assert result.date_received == "2024-06-24"
