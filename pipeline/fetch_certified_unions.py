import csv
import httpx
import itertools
from pathlib import Path

from scrapy import Selector
from slugify import slugify
from .transforms.model import CertifiedUnion

certification_officers_list_current = "https://www.gov.uk/government/publications/official-list-of-trade-unions/current-trade-unions"
certification_officers_list_former = "https://www.gov.uk/government/publications/official-list-of-trade-unions/former-trade-unions"
outfile = Path(__file__).absolute().parent / "data" / "certified_unions.csv"


def get_current_unions():
    r = httpx.get(certification_officers_list_current)
    sel = Selector(text=r.text, type="html")
    canonical_names = sel.css("div.govspeak a::text").getall()
    for canonical_name in canonical_names:
        yield CertifiedUnion(name=canonical_name, id=slugify(canonical_name))


def get_former_unions():
    r = httpx.get(certification_officers_list_former)
    sel = Selector(text=r.text, type="html")
    canonical_names = sel.css("div.govspeak table tbody tr *:is(td, th):first-child::text").getall()
    for canonical_name in canonical_names[1:]:
        trimmed = canonical_name.strip()
        if trimmed:
            yield CertifiedUnion(name=trimmed, id=slugify(trimmed))


with open(outfile, mode="w+") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=CertifiedUnion.model_fields.keys())
    writer.writeheader()
    n = 0
    for tu in itertools.chain(get_current_unions(), get_former_unions()):
        writer.writerow(tu.model_dump())
        n += 1
    print(f"Wrote {n} current and former trade unions to {outfile}")
