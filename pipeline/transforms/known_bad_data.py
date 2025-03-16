def allow_transform_errors(outcome_reference):
    match outcome_reference:
        case "TUR1/1006(2017)":
            return True
        case _:
            return False
