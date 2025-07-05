# labelled_enum.py
"""
A special Enum that plays well with ``pydantic`` and ``mypy``, while allowing human-readable
labels similarly to ``django.db.models.enums.Choices``.

Taken from:
https://github.com/pydantic/pydantic/issues/1401#issuecomment-670223242
"""
from typing import TypeVar, Type
import enum

T = TypeVar("T")


class LabelledEnum(enum.Enum):
    """Enum with labels. Assumes both the value and label are strings."""

    def __new__(cls: Type[T], value: str, label: str) -> T:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
