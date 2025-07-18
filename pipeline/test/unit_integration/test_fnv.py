from pipeline.services.fnv import fnv1a_64


def test_basic_strings():
    """Test basic string hashing functionality."""
    # Test empty string
    assert fnv1a_64("") == 0x4BF29CE484222325

    # Test simple strings
    assert fnv1a_64("a") == 0x2F63DC4C8601EC8C
    assert fnv1a_64("ab") == 0x089C4407B545986A
    assert fnv1a_64("abc") == 0x671FA2190541574B

    # Test longer strings
    assert fnv1a_64("hello") == 0x2430D84680AABD0B
    assert fnv1a_64("world") == 0x4F59FF5E730C8AF3
