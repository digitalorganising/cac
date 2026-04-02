from typing import Any, List, Literal, Optional, Union
from company_disambiguator.hashing import hash_dict
from baml_client.types import OtherEntityType
from pydantic import BaseModel, Field, RootModel, computed_field


class DisambiguateCompanyRequest(BaseModel):
    """Single disambiguation request (excluding candidates)."""

    name: str
    unions: List[str]
    application_date: str
    bargaining_unit: str
    locations: Optional[List[str]] = None


class DisambiguateCompanyLambdaEvent(DisambiguateCompanyRequest):
    """Lambda payload: same fields as DisambiguateCompanyRequest plus ``force`` at the top level."""

    force: bool = False

    def without_force(self) -> DisambiguateCompanyRequest:
        return DisambiguateCompanyRequest.model_validate(
            self.model_dump(exclude={"force"})
        )


class IndustrialClassification(BaseModel):
    """Industrial classification with SIC code details."""

    sic_code: str
    description: str
    section: str


class IdentifiedCompany(BaseModel):
    """Identified company with industrial_classifications instead of sic_codes."""

    type: Literal["identified"] = "identified"
    company_name: str
    company_number: str
    industrial_classifications: List[IndustrialClassification]


class UnidentifiedCompany(BaseModel):
    """Unidentified company result."""

    type: Literal["unidentified"] = "unidentified"
    subtype: OtherEntityType
    company_name: str
    industrial_classifications: List[IndustrialClassification] = []


class DisambiguatedCompany(RootModel):
    """Discriminated union of identified or unidentified company.

    This is a RootModel so the union data can be validated directly.
    Access the wrapped value via the .root property.
    """

    root: Union[IdentifiedCompany, UnidentifiedCompany] = Field(discriminator="type")


# Increment me when you want to invalidate all existing documents
hash_version = 1


def request_to_doc_id(request: DisambiguateCompanyRequest) -> str:
    """Generate document ID from request."""
    return hash_dict({"version": hash_version, **request.model_dump()})


class StoredResult(BaseModel):
    """Document structure stored in Elasticsearch for disambiguated companies.

    Contains both the disambiguation result and the original input request.
    """

    disambiguated_company: DisambiguatedCompany
    input: DisambiguateCompanyRequest
    debug: Optional[dict[str, Any]] = None

    @computed_field
    @property
    def id(self) -> str:
        return request_to_doc_id(self.input)
