import pytest
from scrapers.common.schema import validate, Paper

VALID_PAPER = {
    "id": "iclr-2025-1",
    "title": "Sample Paper",
    "authors": ["Alice"],
    "abstract": "An abstract.",
    "keywords": ["ml"],
    "conference": "ICLR",
    "year": 2025,
    "url": "https://openreview.net/forum?id=abc",
    "presentation": "oral",
}


def test_valid_paper_passes():
    validate(VALID_PAPER)


from pydantic import ValidationError


@pytest.mark.parametrize("missing_field", [
    "id", "title", "authors", "abstract", "keywords",
    "conference", "year", "url",
])
def test_missing_required_field(missing_field):
    paper = {**VALID_PAPER}
    del paper[missing_field]
    with pytest.raises(ValidationError):
        validate(paper)


def test_empty_title_rejected():
    paper = {**VALID_PAPER, "title": ""}
    with pytest.raises(ValidationError):
        validate(paper)


def test_empty_id_rejected():
    paper = {**VALID_PAPER, "id": ""}
    with pytest.raises(ValidationError):
        validate(paper)


def test_unknown_conference_rejected():
    paper = {**VALID_PAPER, "conference": "FOO"}
    with pytest.raises(ValidationError):
        validate(paper)


def test_invalid_presentation_rejected():
    paper = {**VALID_PAPER, "presentation": "keynote"}
    with pytest.raises(ValidationError):
        validate(paper)


def test_presentation_can_be_null():
    paper = {**VALID_PAPER, "presentation": None}
    validate(paper)


def test_year_out_of_range_rejected():
    paper = {**VALID_PAPER, "year": 1900}
    with pytest.raises(ValidationError):
        validate(paper)


def test_empty_keywords_allowed():
    paper = {**VALID_PAPER, "keywords": []}
    validate(paper)


def test_empty_authors_rejected():
    paper = {**VALID_PAPER, "authors": []}
    with pytest.raises(ValidationError):
        validate(paper)
