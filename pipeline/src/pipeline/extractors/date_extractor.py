from dateutil.parser import ParserError
from .. import london_date


def extract_date(statement):
    try:
        date = london_date(statement, fuzzy=True)
        return date.strftime("%Y-%m-%d")
    except ParserError:
        return None
