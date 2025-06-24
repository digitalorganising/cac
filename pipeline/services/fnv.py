def fnv1a_64(string_data, encoding="utf-8"):
    data = string_data.encode(encoding)
    fnv_64_prime = 0x00000100000001B3
    fnv_64_offset_basis = 0xCBF29CE484222325

    hash_val = fnv_64_offset_basis
    for byte in data:
        hash_val = hash_val ^ byte
        hash_val = (hash_val * fnv_64_prime) % 2**64

    return hash_val
