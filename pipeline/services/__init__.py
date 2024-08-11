from tenacity import retry_if_exception, stop_after_attempt, wait_random_exponential


def was_rate_limited(e):
    # TODO replace this with something robust once Boundary have sorted out these types
    return "RateLimited" in str(e)


anthropic_rate_limit = {
    "retry": retry_if_exception(was_rate_limited),
    "wait": wait_random_exponential(min=0, max=90),
    "stop": stop_after_attempt(7),
    "reraise": True,
}
