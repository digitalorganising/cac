import csv
import string
from itertools import chain
from pathlib import Path
from slugify import slugify

from .model import CertifiedUnion, Union

certified_unions_csv = Path(__file__).absolute().parent / ".." / "data" / "certified_unions.csv"


def acronym_candidates(name: str):
    def strip_punctuation(word: str):
        return word.translate(str.maketrans('', '', string.punctuation))

    all_words = list(filter(None, [strip_punctuation(w) for w in name.lower().split() if w not in {"and", "of", "&", "the"}]))

    strings = [
        all_words,
        [w for w in all_words if w != "union"],
        [w for w in all_words if w != "association"],
        [w for w in all_words if w not in {"national", "trade", "union", "workers"}],
    ]
    strings = [s for s in strings if len(s) > 2]

    def ac(words: list[str]):
        return "".join([w[0] for w in words])

    return {ac(w) for w in strings}


class UnionDisambiguator():
    def __init__(self):
        with open(certified_unions_csv, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            certified_unions = (CertifiedUnion.model_validate(row) for row in reader)
            self.certified_unions: dict[str, CertifiedUnion] = {c.name.lower(): c for c in certified_unions}

    def get_unions(self, name: str):
        lc_name = name.lower()

        # Straightforward match
        if lc_name in self.certified_unions:
            cu = self.certified_unions[lc_name]
            return [Union(id=cu.id, label=name, canonical_label=cu.name)]

        # The case where the name needs to be acronymised to match
        for n in acronym_candidates(name):
            if n in self.certified_unions:
                cu = self.certified_unions[n]
                return [Union(id=cu.id, label=name, canonical_label=cu.name)]

        # The case where the name is an acronym of a longer canonical name
        for lc_cert_name, cu in self.certified_unions.items():
            for n in acronym_candidates(lc_cert_name):
                if n == lc_name:
                    return [Union(id=cu.id, label=name, canonical_label=cu.name)]

        # The case where there could be multiple unions
        if ", " in name:
            candidates = name.split(", ")
            return list(chain.from_iterable(self.get_unions(c) for c in candidates))

        if "(" in lc_name:
            paren = lc_name[lc_name.find("(")+1:lc_name.find(")")]
            paren_union = self.get_unions(paren)[0]
            if paren_union.canonical_label:
                return [paren_union.model_copy(update={"label": name})]

        # Giving up
        print(f"HAD TO GIVE UP FOR {name}")
        return [Union(id=slugify(name), label=name, canonical_label=None)]


ud = UnionDisambiguator()
known_names = ['Unite the Union', 'GMB', 'RMT', 'Prospect', 'NEU, NASUWT', 'PCS', 'URTU', 'NUJ', 'UNISON', 'IWGB', 'Community', 'TSSA', 'BFAWU', 'CWU', 'United Voices of the World', 'NEU', 'UCU', 'BECTU', 'Unison', 'NASUWT, NEU', 'PDAU', 'UCATT', 'BMA', 'GMB, Unite the Union', 'IWW', 'National Education Union', 'USDAW', 'Unite', 'AEGIS the Union', 'ASLEF', 'BALPA', 'BMA (British Medical Association)', 'Community Union', 'Equality for Workers Union', 'GMB Scotland', 'IPA', 'IWGB Union', 'Industrial Workers of the World', 'NASUWT, NEU, NAHT', 'Name of PCS', 'Nautilus International', 'PDA', 'PROSPECT', 'UNISON, GMB', 'UVW', 'Union Bank UK plc', 'Workers of England Trade Union']
for n in known_names:
    ud.get_unions(n)
