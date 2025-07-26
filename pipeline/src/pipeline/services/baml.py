import os
from baml_client import b

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
