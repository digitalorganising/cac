import os
import boto3
from baml_client import b
from aws_secretsmanager_caching import SecretCache

env_key = os.getenv("GOOGLE_API_KEY")
secret_name = os.getenv("GOOGLE_API_KEY_SECRET")

session = boto3.Session()
secrets_client = session.client("secretsmanager")
secrets_store = SecretCache(client=secrets_client)

authenticated_client = b.with_options(
    env={"GOOGLE_API_KEY": env_key or secrets_store.get_secret_string(secret_name)}
)
