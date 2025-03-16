# Known bad data

This file documents data which has errors in the source material. Should be reflected in `./transforms/known_bad_data.py`.

[*TUR1/1006(2017)*](https://www.gov.uk/government/publications/cac-outcome-unite-the-union-wheelbase-engineering-ltd) recognition decision has wrong year (2017 rather than 2018) for ballot dates.

[*TUR1/1184(2020)*](https://www.gov.uk/government/publications/cac-outcome-unite-the-union-noble-foods-ltd) the public "last updated" date is wrong, it should be 21st October

[*TUR1/1198(2020)*](https://www.gov.uk/government/publications/cac-outcome-unite-the-union-knapp-uk-ltd) the public "last updated" date is wrong, it should be 16th September (or later)

[*TUR1/1386(2024)*](https://www.gov.uk/government/publications/cac-outcome-community-euro-car-parts-2) the date at the conclusion of the acceptance decision has the wrong year (2023).

## Known issues

These are cases where the way we handle it is wrong

[*TUR1/1202(2020)*](https://www.gov.uk/government/publications/cac-outcome-unite-the-union-wates-living-space) there are effectively 2 acceptance decisions due to the way we treat para 35 decisions as being a type of acceptance decision. Needs some thought.
