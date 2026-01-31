import hashlib
import json
from typing import Any


def hash_dict(data: dict[str, Any]) -> str:
    """Generate a deterministic hash from an arbitrary dictionary.

    This function normalizes the input by:
    - Sorting all list values
    - Sorting dictionary keys
    - Converting to JSON with sorted keys

    Args:
        data: Dictionary to hash

    Returns:
        Truncated 10-character hash of the normalized input
    """
    normalized = _normalize_dict(data)

    # Convert to JSON string with sorted keys for determinism
    hash_string = json.dumps(normalized, sort_keys=True)

    # Generate SHA256 hash and truncate to 10 characters
    hash_bytes = hashlib.sha256(hash_string.encode()).hexdigest()
    return hash_bytes[:10]


def _normalize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively normalize a dictionary by sorting lists and keys.

    Args:
        data: Dictionary to normalize

    Returns:
        Normalized dictionary with sorted lists and keys
    """
    normalized: dict[str, Any] = {}

    # Sort keys and process each value
    for key in sorted(data.keys()):
        value = data[key]

        if isinstance(value, dict):
            # Recursively normalize nested dictionaries
            normalized[key] = _normalize_dict(value)
        elif isinstance(value, list):
            # Sort list items (recursively normalize if they're dicts)
            normalized_list = []
            for item in value:
                if isinstance(item, dict):
                    normalized_list.append(_normalize_dict(item))
                else:
                    normalized_list.append(item)
            normalized[key] = sorted(normalized_list)
        else:
            # Primitive value, keep as-is
            normalized[key] = value

    return normalized
