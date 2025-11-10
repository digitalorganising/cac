def fix_extracted_data(data):
    match data:
        case "TUR1/1006(2017)":
            # Ballot dates have the wrong year
            data.ballot.start_ballot_period = data.ballot.start_ballot_period.replace(
                "2017", "2018"
            )
            data.ballot.end_ballot_period = data.ballot.end_ballot_period.replace(
                "2017", "2018"
            )
            return data
        case "TUR1/1198(2020)":
            # Public "last updated" date is wrong
            data.last_updated = "2020-09-16"
            return data
        case "TUR1/1184(2020)":
            # Public "last updated" date is wrong
            data.last_updated = "2020-10-21"
            return data
        case _:
            return data


def override_reference(outcome_reference):
    match outcome_reference:
        case "TUR1/913(2014)":
            return "TUR1/0913(2015)"
        case "https://www.gov.uk/government/publications/cac-outcome-bectu-institute-of-contemporary-arts":
            return "TUR1/0924(2015)"
        case "https://www.gov.uk/government/publications/cac-outcome-gmb-green-team-services-limited":
            return "TUR1/0920(2015)"
        case "https://www.gov.uk/government/publications/cac-outcome-prospect-exeter-airport":
            return "TUR1/1058(2018)"
        case "https://www.gov.uk/government/publications/cac-outcome-unison-deepdene-care":
            return "TUR1/0911(2015)"
        case "https://www.gov.uk/government/publications/cac-outcome-unite-the-union-precision-polymer-engineering":
            return "TUR1/0969(2016)"
        case "https://www.gov.uk/government/publications/cac-outcome-urtu-utl-consumer-solutions":
            return "TUR1/0926(2015)"
        case _:
            return outcome_reference
