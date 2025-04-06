from dateutil.parser import parse as dateparse, ParserError


def extract_date(statement):
    try:
        date = dateparse(statement, fuzzy=True)
        return date.strftime("%Y-%m-%d")
    except ParserError:
        return None
