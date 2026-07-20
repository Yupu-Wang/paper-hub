import pytest
from scrapers.common import openreview_client
from scrapers.common.openreview_client import parse_presentation, is_accepted, _client


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


class _FakeOpenReviewClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_client_is_anonymous_when_no_credentials_env(monkeypatch):
    monkeypatch.delenv("OPENREVIEW_USERNAME", raising=False)
    monkeypatch.delenv("OPENREVIEW_PASSWORD", raising=False)
    monkeypatch.setattr(openreview_client.openreview.api, "OpenReviewClient", _FakeOpenReviewClient)

    client = _client()

    assert "username" not in client.kwargs
    assert "password" not in client.kwargs


def test_client_is_authenticated_when_credentials_env_set(monkeypatch):
    monkeypatch.setenv("OPENREVIEW_USERNAME", "alice@example.com")
    monkeypatch.setenv("OPENREVIEW_PASSWORD", "hunter2")
    monkeypatch.setattr(openreview_client.openreview.api, "OpenReviewClient", _FakeOpenReviewClient)

    client = _client()

    assert client.kwargs["username"] == "alice@example.com"
    assert client.kwargs["password"] == "hunter2"
