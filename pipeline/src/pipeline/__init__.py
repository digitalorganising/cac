from dateutil.parser import parse as date_parse
from dateutil.utils import default_tzinfo
from dateutil.tz import gettz


def london_date(date_str: str, **parse_kwargs):
    london_tz = gettz("Europe/London")
    return default_tzinfo(
        date_parse(date_str, dayfirst=True, **parse_kwargs), london_tz
    )
