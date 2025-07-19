def fnv1a_64(string_data, encoding="utf-8"):
    data = string_data.encode(encoding)
    fnv_64_prime = 0x00000100000001B3
    fnv_64_offset_basis = 0xCBF29CE484222325

    hash_val = fnv_64_offset_basis
    for byte in data:
        hash_val = hash_val ^ byte
        hash_val = (hash_val * fnv_64_prime) % 2**64

    return to_signed_64(hash_val)


def to_signed_64(hash_val):
    return hash_val - 2**63 if hash_val >= 2**63 else hash_val
