import os
from baml_client import b
from baml_py.errors import BamlValidationError
from baml_py import ClientRegistry
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
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
        def wrapper(*args, **kwargs):
            attempt = 0

            @retry(
                retry=retry_if_exception_type(BamlValidationError),
                stop=stop_after_attempt(max_attempts),
                wait=wait,
                reraise=True,
            )
            def _retry_func():
                nonlocal attempt
                attempt += 1
                if attempt == max_attempts:
                    return func(*args, **kwargs, client=retry_client)
                elif attempt > max_attempts:
                    raise RuntimeError("You shouldn't be seeing this error!")
                return func(*args, **kwargs, client=default_client)

            return _retry_func()

        return wrapper

    return decorator
