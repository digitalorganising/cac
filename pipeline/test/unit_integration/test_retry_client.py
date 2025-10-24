import os
import pytest
from tenacity import wait_none
from baml_py.errors import BamlValidationError


@pytest.fixture(scope="module", autouse=True)
def set_env():
    os.environ["GOOGLE_API_KEY"] = "1234567890"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


def make_rotating_func(*funcs):
    """
    Returns a function that calls each of the given functions sequentially
    on successive invocations. Once all have been called, raises RuntimeError.
    """

    def gen():
        for func in funcs:
            yield func
        # After exhausting all funcs, raise on further calls
        while True:
            raise RuntimeError("All provided functions have already been called.")

    iterator = gen()

    def wrapper(*args, **kwargs):
        func = next(iterator)
        return func(*args, **kwargs)

    return wrapper


def test_retry_client():
    from pipeline.services.baml import (
        authenticated_client,
        large_client,
        with_retry_client,
    )

    def first_call(key, *, client):
        assert key == 1
        assert client is authenticated_client, "client was not the default client"

    def second_call(key, *, client):
        assert key == 2
        assert client is authenticated_client, "client was not the default client"
        raise BamlValidationError(
            message="test error",
            raw_output="test output",
            detailed_message="test detailed message",
            prompt="test prompt",
        )

    def third_call(key, *, client):
        assert key == 2
        assert client is large_client, "client was not the retry client"

    def fourth_call(key, *, client):
        assert key == 3
        assert client is authenticated_client, "client was not the default client"

    test_func = with_retry_client(authenticated_client, large_client, wait=wait_none())(
        make_rotating_func(first_call, second_call, third_call, fourth_call)
    )

    test_func(key=1)
    test_func(key=2)
    test_func(key=3)
    with pytest.raises(RuntimeError) as e:
        test_func(key=4)
        assert e.value.message == "All provided functions have already been called."
