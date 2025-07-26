import boto3
from aws_secretsmanager_caching import SecretCache

session = boto3.Session()
secrets_client = session.client("secretsmanager")
secrets_store = SecretCache(client=secrets_client)
