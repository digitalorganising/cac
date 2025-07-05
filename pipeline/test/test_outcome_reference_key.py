from pipeline.transforms import outcome_reference_key


def test_outcome_reference_key_different_years():
    """Test outcome_reference_key with different years"""
    test_cases = [
        ("TUR1/123(2017)", "TUR1/0123(2017)"),
        ("TUR1/0123(2017)", "TUR1/0123(2017)"),
        ("TUR1/456(2018)", "TUR1/0456(2018)"),
        ("TUR1/789(2019)", "TUR1/0789(2019)"),
        ("TUR1/1006(2020)", "TUR1/1006(2020)"),
        ("TUR1/1184(2021)", "TUR1/1184(2021)"),
        ("TUR1/1198(2022)", "TUR1/1198(2022)"),
        ("TUR1/1386(2023)", "TUR1/1386(2023)"),
        ("TUR1/1394(2024)", "TUR1/1394(2024)"),
    ]

    for input_ref, expected in test_cases:
        doc = {"reference": input_ref}
        result = outcome_reference_key(doc)
        assert (
            result == expected
        ), f"Failed for {input_ref}: expected {expected}, got {result}"
