import os
import pytest
from tenacity import wait_none
from baml_py.errors import BamlValidationError


@pytest.fixture(scope="module", autouse=True)
def set_env():
    os.environ["GOOGLE_API_KEY"] = "1234567890"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


def test_retry_client():
    from pipeline.services.baml import (
        authenticated_client,
        large_client,
        with_retry_client,
    )

    did_raise = False

    @with_retry_client(authenticated_client, large_client, wait=wait_none())
    def stub_test_func(a, b, *, client):
        nonlocal did_raise
        if did_raise:
            assert client is large_client
        else:
            assert client is authenticated_client
            did_raise = True
            raise BamlValidationError(
                message="test error",
                raw_output="test output",
                detailed_message="test detailed message",
                prompt="test prompt",
            )

    stub_test_func(1, 2)
