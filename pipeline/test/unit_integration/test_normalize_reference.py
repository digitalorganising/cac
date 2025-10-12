from pipeline.transforms import normalize_reference


def test_normalize_reference_different_years():
    """Test normalize_reference with different years"""
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
        ("TUR1/ 911(2015)", "TUR1/0911(2015)"),
    ]

    for input_ref, expected in test_cases:
        result = normalize_reference(input_ref)
        assert (
            result == expected
        ), f"Failed for {input_ref}: expected {expected}, got {result}"
