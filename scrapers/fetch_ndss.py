from __future__ import annotations
import argparse
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from tqdm import tqdm

from scrapers.common.ndss import parse_index, parse_paper_page
from scrapers.common.schema import validate

log = logging.getLogger(__name__)
CST = timezone(timedelta(hours=8))

USER_AGENT = "paper-hub-scraper/1.0 (+https://github.com/Yupu-Wang/paper-hub)"


def get(url: str, retries: int = 3) -> str:
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            log.warning("retry %s in %ds: %s", url, wait, e)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def fetch(year: int) -> dict:
    index_url = f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/"
    index_html = get(index_url)
    entries = parse_index(index_html)
    log.info("found %d papers in index", len(entries))

    papers = []
    for i, entry in enumerate(tqdm(entries, desc=f"NDSS {year}"), start=1):
        try:
            meta = parse_paper_page(get(entry["url"]))
            paper = {
                "id": f"ndss-{year}-{i}",
                "title": entry["title"],
                "authors": meta["authors"],
                "abstract": meta["abstract"],
                "keywords": [],
                "conference": "NDSS",
                "year": year,
                "url": entry["url"],
                "presentation": None,
            }
            validate(paper)
            papers.append(paper)
            time.sleep(0.1)  # gentle pacing
        except Exception as e:
            log.warning("skip %s: %s", entry["url"], e)

    return {
        "conference": "NDSS",
        "year": year,
        "fetched_at": datetime.now(CST).isoformat(timespec="seconds"),
        "source": "ndss-symposium.org",
        "papers": papers,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    result = fetch(args.year)
    out = args.output or Path(f"data/raw/ndss-{args.year}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Wrote {len(result['papers'])} papers to {out}")


if __name__ == "__main__":
    main()
