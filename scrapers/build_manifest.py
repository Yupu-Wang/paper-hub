from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

CST = timezone(timedelta(hours=8))


def build_manifest(shards_dir: Path, output: Path) -> None:
    entries = []
    for path in sorted(shards_dir.glob("*.json")):
        shard = json.loads(path.read_text())
        entries.append({
            "conference": shard["conference"],
            "year": shard["year"],
            "count": shard["count"],
            "file": f"shards/{path.name}",
            "size_bytes": path.stat().st_size,
        })
    manifest = {
        "built_at": datetime.now(CST).isoformat(timespec="seconds"),
        "shards": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards-dir", type=Path, default=Path("data/shards"))
    ap.add_argument("--output", type=Path, default=Path("data/manifest.json"))
    args = ap.parse_args()
    build_manifest(args.shards_dir, args.output)
    print(f"Wrote manifest: {args.output}")


if __name__ == "__main__":
    main()
