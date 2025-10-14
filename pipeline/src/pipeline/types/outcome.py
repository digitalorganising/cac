from datetime import datetime
from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    ValidationError,
    model_validator,
)
from typing import get_args, Optional, Union, Self

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
    documents: dict[DocumentType, Optional[str]]
    document_urls: dict[DocumentType, Optional[str]]
    extracted_data: dict[
        DocumentType, ExtractedData
    ]  # Not fully typesafe but doesn't really matter

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        try:
            return handler(data)
        except ValidationError as e:
            print(
                f"Outcome validation failed for {data.get('id', 'unknown')} ({data.get('outcome_url', 'unknown')})"
            )
            raise
