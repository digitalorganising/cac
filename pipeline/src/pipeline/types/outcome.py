from datetime import datetime
from pydantic import BaseModel
from typing import get_args, Union

from .documents import DocumentType
from .decisions import DecisionAugmented

ExtractedData = Union[
    tuple(
        D.model_fields["extracted_data"].annotation
        for D in get_args(DecisionAugmented.model_fields["root"].annotation)
    )
]


class Outcome(BaseModel):
    id: str
    last_updated: datetime
    outcome_url: str
    outcome_title: str
    documents: dict[DocumentType, str]
    document_urls: dict[DocumentType, str]
    extracted_data: dict[
        DocumentType, ExtractedData
    ]  # Not fully typesafe but doesn't really matter
