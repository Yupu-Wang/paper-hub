from __future__ import annotations
import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from scrapers.common.schema import validate

log = logging.getLogger(__name__)
CST = timezone(timedelta(hours=8))


def content_hash(data) -> str:
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()[:6]


def build(raw_path: Path, shards_dir: Path) -> Path:
    raw = json.loads(raw_path.read_text())
    conf = raw["conference"].lower()
    year = raw["year"]
    papers = []
    for p in raw["papers"]:
        try:
            validate(p)
            papers.append(p)
        except Exception as e:
            log.warning("drop invalid paper %s: %s", p.get("id"), e)
    h = content_hash(papers)
    shard = {
        "conference": raw["conference"],
        "year": year,
        "count": len(papers),
        "built_at": datetime.now(CST).isoformat(timespec="seconds"),
        "papers": papers,
    }
    shards_dir.mkdir(parents=True, exist_ok=True)
    out = shards_dir / f"{conf}-{year}.{h}.json"
    for old in shards_dir.glob(f"{conf}-{year}.*.json"):
        if old != out:
            old.unlink()
    out.write_text(json.dumps(shard, ensure_ascii=False))
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    ap.add_argument("--shards-dir", type=Path, default=Path("data/shards"))
    args = ap.parse_args()

    raw_path = args.raw_dir / f"{args.conf}-{args.year}.json"
    out = build(raw_path, args.shards_dir)
    print(f"Built shard: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
