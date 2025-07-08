from dateutil.parser import parse as date_parse


def merge_withdrawal(withdrawal, outcome):
    print("UFKC", withdrawal)
    withdrawal_date = date_parse(
        withdrawal["application_withdrawn"], dayfirst=True  # God save the Queen
    )

    outcome["extracted_data"]["application_withdrawn"] = {
        "decision_date": withdrawal_date.isoformat()[:10],
    }

    if (
        "application_received" not in outcome["extracted_data"]
        and "acceptance_decision" not in outcome["extracted_data"]
    ):
        application_received_date = date_parse(
            withdrawal["application_received"], dayfirst=True
        )
        outcome["extracted_data"]["application_received"] = {
            "decision_date": application_received_date.isoformat()[:10],
        }

    return outcome
