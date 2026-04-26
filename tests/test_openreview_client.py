import pytest
from scrapers.common.openreview_client import parse_presentation, is_accepted


@pytest.mark.parametrize("decision,expected", [
    # legacy decision strings
    ("Accept (oral)", "oral"),
    ("Accept (Oral)", "oral"),
    ("Accept (spotlight)", "spotlight"),
    ("Accept (Spotlight)", "spotlight"),
    ("Accept (poster)", "poster"),
    ("Accept", "poster"),
    ("Reject", None),
    ("", None),
    (None, None),
    # v2 API venue strings
    ("ICLR 2025 Oral", "oral"),
    ("ICLR 2025 Spotlight", "spotlight"),
    ("ICLR 2025 Poster", "poster"),
    ("NeurIPS 2024 Oral", "oral"),
])
def test_parse_presentation(decision, expected):
    assert parse_presentation(decision) == expected


@pytest.mark.parametrize("decision,expected", [
    ("Accept (oral)", True),
    ("Accept (poster)", True),
    ("Accept", True),
    ("Reject", False),
    ("Withdrawn", False),
    ("", False),
    (None, False),
])
def test_is_accepted(decision, expected):
    assert is_accepted(decision) == expected
