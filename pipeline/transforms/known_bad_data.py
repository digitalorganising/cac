def allow_transform_errors(outcome_reference):
    match outcome_reference:
        case "TUR1/1006(2017)" | "TUR1/1202(2020)" | "TUR1/1386(2024)":
            return True
        case _:
            return False
