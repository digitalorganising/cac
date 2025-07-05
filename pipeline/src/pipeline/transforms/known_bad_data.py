def allow_transform_errors(outcome_reference):
    match outcome_reference:
        case "TUR1/1006(2017)" | "TUR1/1202(2020)" | "TUR1/1386(2024)":
            return True
        case _:
            return False


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
