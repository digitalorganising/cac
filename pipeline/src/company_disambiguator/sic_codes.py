import json
import logging
from typing import List, Union
from company_disambiguator.model import (
    IndustrialClassification,
    IdentifiedCompany,
    UnidentifiedCompany,
    DisambiguatedCompany,
)
from baml_client.types import (
    IdentifiedCompany as BamlIdentifiedCompany,
    UnidentifiedCompany as BamlUnidentifiedCompany,
)

# Load SIC codes mapping at module level
SIC_CODES_PATH = "./company_disambiguator/data/sic_codes.json"
SIC_CODES_MAPPING: dict[str, dict[str, str]] = {}

try:
    with open(SIC_CODES_PATH, "r") as f:
        SIC_CODES_MAPPING = json.load(f)
except FileNotFoundError:
    logging.warning(f"SIC codes file not found at {SIC_CODES_PATH}")
except Exception as e:
    logging.error(f"Failed to load SIC codes: {e}")


def transform_sic_codes(sic_codes: List[str]) -> List[IndustrialClassification]:
    """Transform SIC codes to industrial_classifications.

    Args:
        sic_codes: List of SIC code strings

    Returns:
        List of industrial classification objects with sic_code, description, section
    """
    industrial_classifications = []

    for sic_code in sic_codes:
        if sic_code in SIC_CODES_MAPPING:
            classification = IndustrialClassification(
                sic_code=sic_code,
                description=SIC_CODES_MAPPING[sic_code].get("description", ""),
                section=SIC_CODES_MAPPING[sic_code].get("section", ""),
            )
            industrial_classifications.append(classification)
        else:
            logging.warning(f"SIC code {sic_code} not found in mapping, dropping")

    return industrial_classifications


def transform_baml_result(
    result: Union[BamlIdentifiedCompany, BamlUnidentifiedCompany],
    company_name: str,
) -> DisambiguatedCompany:
    """Transform BAML result to use industrial_classifications instead of sic_codes.

    Args:
        result: BAML result (IdentifiedCompany or UnidentifiedCompany)
        company_name: The company name from the request

    Returns:
        Transformed result with industrial_classifications for identified companies
    """
    if isinstance(result, BamlIdentifiedCompany):
        # Transform sic_codes to industrial_classifications
        industrial_classifications = transform_sic_codes(result.sic_codes)

        return IdentifiedCompany(
            company_name=company_name,
            company_number=result.company_number,
            industrial_classifications=industrial_classifications,
        )
    else:
        # UnidentifiedCompany doesn't need transformation
        return UnidentifiedCompany(company_name=company_name)
