from dateutil.parser import parse


def date_eq(a, b):
    da = parse(a)
    db = parse(b)
    return da == db
