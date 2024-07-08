from dateutil.parser import parse as dateparse


def extract_date(statement):
    date = dateparse(statement, fuzzy=True)
    return date.strftime("%Y-%m-%d")
