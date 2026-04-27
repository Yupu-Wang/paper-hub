from typing import Literal
from pydantic import BaseModel, Field

Conference = Literal["ICLR", "ICML", "NeurIPS", "NDSS", "AAAI"]
Presentation = Literal["oral", "spotlight", "poster"]


class Paper(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    authors: list[str] = Field(min_length=1)
    abstract: str
    keywords: list[str]
    conference: Conference
    year: int = Field(ge=2000, le=2100)
    url: str = Field(min_length=1)
    presentation: Presentation | None


def validate(paper: dict) -> Paper:
    """Raise pydantic.ValidationError if invalid; return parsed Paper otherwise."""
    return Paper(**paper)
