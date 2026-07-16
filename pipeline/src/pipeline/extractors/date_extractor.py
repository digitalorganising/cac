from dateutil.parser import ParserError, isoparse

from .. import london_date


def extract_date(statement):
    words = statement.split()
    if words:
        try:
            isoparse(words[-1])
        except (ValueError, TypeError):
            pass
        else:
            return london_date(words[-1], dayfirst=False).strftime("%Y-%m-%d")

    try:
        return london_date(statement, fuzzy=True).strftime("%Y-%m-%d")
    except ParserError:
        return None
