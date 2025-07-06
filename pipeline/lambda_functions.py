import lambdas.scrape_all_outcomes as scrape_all_outcomes


def scrape_all_outcomes_handler(event, context):
    return scrape_all_outcomes.handler(event, context)
