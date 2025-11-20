import os
from baml_client import b
from baml_py.errors import BamlValidationError
from baml_py import ClientRegistry
from tenacity import (
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    AsyncRetrying,
)
from .secrets import secrets_store

env_key = os.getenv("GOOGLE_API_KEY")
secret_name = os.getenv("GOOGLE_API_KEY_SECRET")


def _get_api_key():
    if env_key:
        return env_key
    if secret_name:
        return secrets_store.get_secret_string(secret_name)
    return None


authenticated_client = b.with_options(env={"GOOGLE_API_KEY": _get_api_key()})

large_client_registry = ClientRegistry()
large_client_registry.set_primary("LargeClient")
large_client = authenticated_client.with_options(client_registry=large_client_registry)


def with_retry_client(default_client, retry_client, wait=wait_fixed(3), max_attempts=2):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async for attempt_ctx in AsyncRetrying(
                retry=retry_if_exception_type(BamlValidationError),
                stop=stop_after_attempt(max_attempts),
                wait=wait,
                reraise=True,
            ):
                with attempt_ctx:
                    attempt_number = attempt_ctx.retry_state.attempt_number
                    if attempt_number == max_attempts:
                        print("Using retry client")
                        return await func(*args, **kwargs, client=retry_client)
                    return await func(*args, **kwargs, client=default_client)

        return async_wrapper

    return decorator
