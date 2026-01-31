from typing import List, Literal, Optional, Union
from company_disambiguator.operations import request_to_doc_id
from pydantic import BaseModel, Field, RootModel, computed_field


class DisambiguateCompanyRequest(BaseModel):
    """Single disambiguation request (excluding candidates)."""

    name: str
    unions: List[str]
    application_date: str
    bargaining_unit: str
    locations: Optional[List[str]] = None


class DisambiguateCompanyEvent(BaseModel):
    """Batch event containing multiple disambiguation requests."""

    requests: List[DisambiguateCompanyRequest]


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
    company_name: str


class DisambiguatedCompany(RootModel):
    """Discriminated union of identified or unidentified company.

    This is a RootModel so the union data can be validated directly.
    Access the wrapped value via the .root property.
    """

    root: Union[IdentifiedCompany, UnidentifiedCompany] = Field(discriminator="type")


class StoredResult(BaseModel):
    """Document structure stored in Elasticsearch for disambiguated companies.

    Contains both the disambiguation result and the original input request.
    """

    disambiguated_company: DisambiguatedCompany
    input: DisambiguateCompanyRequest
    debug: Optional[dict[str, str]] = None

    @computed_field
    @property
    def id(self) -> str:
        return request_to_doc_id(self.input)
