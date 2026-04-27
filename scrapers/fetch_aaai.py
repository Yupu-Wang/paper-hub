from __future__ import annotations
import argparse
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from tqdm import tqdm

from scrapers.common.aaai import (
    parse_archive_for_year,
    parse_issue_articles,
    parse_paper_abstract,
)
from scrapers.common.schema import validate

log = logging.getLogger(__name__)
CST = timezone(timedelta(hours=8))

ARCHIVE_URL = "https://ojs.aaai.org/index.php/AAAI/issue/archive"
USER_AGENT = "paper-hub-scraper/1.0 (+https://github.com/Yupu-Wang/paper-hub)"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _get(s: requests.Session, url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            r = s.get(url, timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def fetch(year: int, workers: int = 8) -> dict:
    s = _session()

    # Phase 1: archive → issue URLs
    archive_html = _get(s, ARCHIVE_URL)
    issue_urls = parse_archive_for_year(archive_html, year)
    log.info("found %d issues for AAAI %d", len(issue_urls), year)
    if not issue_urls:
        raise SystemExit(f"No AAAI-{str(year)[-2:]} issues found in OJS archive")

    # Phase 2: each issue → article entries (sequential, only 25 requests)
    entries: list[dict] = []
    for url in tqdm(issue_urls, desc="AAAI issues"):
        entries.extend(parse_issue_articles(_get(s, url)))
    log.info("found %d articles total", len(entries))

    # Phase 3: parallel fetch detail pages for abstracts
    def fetch_abstract(entry):
        try:
            return entry["url"], parse_paper_abstract(_get(s, entry["url"]))
        except Exception as e:
            log.warning("skip %s: %s", entry["url"], e)
            return entry["url"], None

    abstracts: dict[str, str | None] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fetch_abstract, e) for e in entries]
        for f in tqdm(as_completed(futures), total=len(futures), desc=f"AAAI {year} abstracts"):
            url, abstract = f.result()
            abstracts[url] = abstract

    # Phase 4: build & validate paper objects
    papers = []
    for i, e in enumerate(entries, start=1):
        abstract = abstracts.get(e["url"])
        if abstract is None:
            continue
        paper = {
            "id": f"aaai-{year}-{i}",
            "title": e["title"],
            "authors": e["authors"],
            "abstract": abstract,
            "keywords": [],
            "conference": "AAAI",
            "year": year,
            "url": e["url"],
            "presentation": None,
        }
        try:
            validate(paper)
            papers.append(paper)
        except Exception as ex:
            log.warning("drop invalid %s: %s", paper["id"], ex)

    return {
        "conference": "AAAI",
        "year": year,
        "fetched_at": datetime.now(CST).isoformat(timespec="seconds"),
        "source": "ojs.aaai.org",
        "papers": papers,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    result = fetch(args.year, workers=args.workers)
    out = args.output or Path(f"data/raw/aaai-{args.year}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Wrote {len(result['papers'])} papers to {out}")


if __name__ == "__main__":
    main()
