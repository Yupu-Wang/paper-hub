from __future__ import annotations
import os
from typing import Iterator

import openreview
from tqdm import tqdm


def is_accepted(decision: str | None) -> bool:
    """Check legacy-style decision string (e.g., 'Accept (oral)')."""
    if not decision:
        return False
    return decision.strip().lower().startswith("accept")


def parse_presentation(decision: str | None) -> str | None:
    """Extract presentation type from a decision string.

    Accepts both legacy 'Accept (oral)' and v2 venue-style 'ICLR 2025 Oral'.
    Returns 'oral' / 'spotlight' / 'poster' / None.
    """
    if not decision:
        return None
    d = decision.lower()
    if "oral" in d:
        return "oral"
    if "spotlight" in d:
        return "spotlight"
    # Legacy: 'Accept' or 'Accept (poster)' → poster
    if is_accepted(decision):
        return "poster"
    # v2 venue: 'ICLR 2025 Poster' → poster
    if "poster" in d:
        return "poster"
    return None


def _client() -> openreview.api.OpenReviewClient:
    username = os.environ.get("OPENREVIEW_USERNAME")
    password = os.environ.get("OPENREVIEW_PASSWORD")
    if username and password:
        return openreview.api.OpenReviewClient(
            baseurl="https://api2.openreview.net", username=username, password=password
        )
    return openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")


def fetch_venue_papers(venue_id: str) -> Iterator[dict]:
    """Yield raw note dicts for accepted papers in a venue.

    venue_id is like 'ICLR.cc/2025/Conference'. The API returns only
    accepted papers when filtered by venueid.
    """
    client = _client()
    notes = client.get_all_notes(content={"venueid": venue_id})
    for n in tqdm(notes, desc=f"Fetching {venue_id}"):
        c = n.content
        venue = (c.get("venue") or {}).get("value", "")
        yield {
            "forum_id": n.id,
            "title": (c.get("title") or {}).get("value", ""),
            "authors": (c.get("authors") or {}).get("value", []),
            "abstract": (c.get("abstract") or {}).get("value", ""),
            "keywords": (c.get("keywords") or {}).get("value", []),
            "decision": venue,
        }
