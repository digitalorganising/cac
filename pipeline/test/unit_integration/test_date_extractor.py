from pipeline.extractors.date_extractor import extract_date


def test_application_received():
    statement = (
        "This application was received on 24 June 2024,"
        "and no decisions have yet been issued."
    )
    result = extract_date(statement)
    assert result == "2024-06-24"


def test_case_closed():
    statement = "This case was closed on 6 March 2019."
    result = extract_date(statement)
    assert result == "2019-03-06"
