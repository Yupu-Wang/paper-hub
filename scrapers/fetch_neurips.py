from __future__ import annotations
import argparse
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from scrapers.common.openreview_client import fetch_venue_papers, parse_presentation
from scrapers.common.schema import validate

log = logging.getLogger(__name__)
CST = timezone(timedelta(hours=8))

# NeurIPS 2023+ uses OpenReview. For 2021-2022 the data lives only on
# papers.nips.cc and would need a separate scraper — add when needed.


def fetch(year: int) -> dict:
    if year < 2023:
        raise SystemExit(
            f"NeurIPS {year} is not on OpenReview. papers.nips.cc path not yet implemented."
        )
    venue_id = f"NeurIPS.cc/{year}/Conference"
    raw_papers = list(fetch_venue_papers(venue_id))
    papers = []
    for i, p in enumerate(raw_papers, start=1):
        paper = {
            "id": f"neurips-{year}-{i}",
            "title": p["title"].strip(),
            "authors": p["authors"],
            "abstract": p["abstract"].strip(),
            "keywords": p["keywords"],
            "conference": "NeurIPS",
            "year": year,
            "url": f"https://openreview.net/forum?id={p['forum_id']}",
            "presentation": parse_presentation(p["decision"]),
        }
        try:
            validate(paper)
            papers.append(paper)
        except Exception as e:
            log.warning("Skipping paper %s: %s", paper["id"], e)
    return {
        "conference": "NeurIPS",
        "year": year,
        "fetched_at": datetime.now(CST).isoformat(timespec="seconds"),
        "source": "openreview",
        "papers": papers,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    result = fetch(args.year)
    out = args.output or Path(f"data/raw/neurips-{args.year}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Wrote {len(result['papers'])} papers to {out}")


if __name__ == "__main__":
    main()
