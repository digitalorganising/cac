import json
from typing import Optional, Tuple, Union, Dict, Any

import boto3
from opensearchpy import (
    AsyncOpenSearch,
    OpenSearch,
    AWSV4SignerAuth,
    AWSV4SignerAsyncAuth,
    exceptions,
    AsyncHttpConnection,
    RequestsHttpConnection,
)


def get_auth(
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> Union[Tuple[str, str], Dict[str, Any]]:
    """Get authentication credentials for OpenSearch.

    Args:
        user: Optional username for basic auth
        password: Optional password for basic auth

    Returns:
        Either a tuple of (username, password) for basic auth or a dict of AWS auth arguments
    """
    if user:
        return (user, password)
    else:
        session = boto3.Session()
        return {
            "credentials": session.get_credentials(),
            "region": session.region_name,
            "service": "es",
        }


def create_client(
    cluster_host: str,
    auth: Union[Tuple[str, str], Dict[str, Any]],
    async_client: bool = True,
    **kwargs,
) -> Union[AsyncOpenSearch, OpenSearch]:
    """Create an OpenSearch client with common configuration.

    Args:
        cluster_host: The OpenSearch cluster host URL
        auth: Authentication credentials from get_auth()
        async_client: Whether to create an async client
        **kwargs: Additional client configuration options

    Returns:
        An OpenSearch client instance
    """
    client_class = AsyncOpenSearch if async_client else OpenSearch

    # Convert auth arguments to appropriate auth class
    if isinstance(auth, tuple):
        http_auth = auth
    else:
        auth_class = AWSV4SignerAsyncAuth if async_client else AWSV4SignerAuth
        http_auth = auth_class(**auth)

    return client_class(
        hosts=[cluster_host],
        use_ssl=("https" in cluster_host),
        http_auth=http_auth,
        http_compress=True,
        request_timeout=60,
        timeout=60,
        connection_class=(
            AsyncHttpConnection if async_client else RequestsHttpConnection
        ),
        **kwargs,
    )


async def ensure_index_mapping(
    client: AsyncOpenSearch,
    index: str,
    mapping_path: Optional[str],
) -> None:
    """Ensure an index exists with the specified mapping.

    Args:
        client: OpenSearch client
        index: Name of the index
        mapping_path: Path to JSON mapping file
    """
    if not mapping_path:
        return

    try:
        with open(mapping_path) as f:
            mapping = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load mapping from {mapping_path}: {e}")
        raise RuntimeError(f"Failed to load mapping from {mapping_path}: {e}") from e

    try:
        # Check if index exists
        exists = await client.indices.exists(index=index)

        if not exists:
            # Create index with mapping
            print(f"Creating index {index} with mapping from {mapping_path}")
            await client.indices.create(index=index, body={"mappings": mapping})
        else:
            # Update existing index mapping
            await client.indices.put_mapping(index=index, body=mapping)
    except exceptions.OpenSearchException as e:
        if "resource_already_exists_exception" in str(e):
            # This is due to a race condition where the index is created after the exists check
            return
        print(f"Failed to ensure index mapping: {e}")
        raise RuntimeError(f"Failed to ensure index mapping: {e}") from e
