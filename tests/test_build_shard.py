import json
from pathlib import Path
from scrapers.build_shard import build, content_hash


def test_content_hash_stable():
    data = {"a": 1, "b": [1, 2, 3]}
    h1 = content_hash(data)
    h2 = content_hash(data)
    assert h1 == h2
    assert len(h1) == 6
    assert h1.isalnum()


def test_build_writes_shard_and_returns_filename(tmp_path):
    raw = {
        "conference": "ICLR",
        "year": 2025,
        "fetched_at": "2026-04-26T15:30:00+08:00",
        "source": "openreview",
        "papers": [
            {
                "id": "iclr-2025-1",
                "title": "Test",
                "authors": ["A"],
                "abstract": "abs",
                "keywords": [],
                "conference": "ICLR",
                "year": 2025,
                "url": "https://openreview.net/forum?id=x",
                "presentation": "oral",
            }
        ],
    }
    raw_path = tmp_path / "iclr-2025.json"
    raw_path.write_text(json.dumps(raw))
    shards_dir = tmp_path / "shards"

    out = build(raw_path, shards_dir)
    assert out.exists()
    assert out.parent == shards_dir
    assert out.name.startswith("iclr-2025.")
    assert out.name.endswith(".json")

    shard = json.loads(out.read_text())
    assert shard["conference"] == "ICLR"
    assert shard["year"] == 2025
    assert shard["count"] == 1
    assert shard["papers"][0]["id"] == "iclr-2025-1"


def test_build_rejects_invalid_paper(tmp_path):
    raw = {
        "conference": "ICLR",
        "year": 2025,
        "fetched_at": "2026-04-26T15:30:00+08:00",
        "source": "openreview",
        "papers": [{"id": "bad", "title": ""}],
    }
    raw_path = tmp_path / "iclr-2025.json"
    raw_path.write_text(json.dumps(raw))
    shards_dir = tmp_path / "shards"
    out = build(raw_path, shards_dir)
    shard = json.loads(out.read_text())
    assert shard["count"] == 0


def test_build_replaces_old_hash_versions(tmp_path):
    """Building twice with different content keeps only the latest version."""
    raw = {
        "conference": "ICLR",
        "year": 2025,
        "fetched_at": "2026-04-26T15:30:00+08:00",
        "source": "openreview",
        "papers": [{
            "id": "iclr-2025-1", "title": "v1", "authors": ["A"],
            "abstract": "abs", "keywords": [], "conference": "ICLR",
            "year": 2025, "url": "https://x", "presentation": None,
        }],
    }
    raw_path = tmp_path / "iclr-2025.json"
    raw_path.write_text(json.dumps(raw))
    shards_dir = tmp_path / "shards"
    out1 = build(raw_path, shards_dir)
    raw["papers"][0]["title"] = "v2"
    raw_path.write_text(json.dumps(raw))
    out2 = build(raw_path, shards_dir)
    assert out2.exists()
    assert not out1.exists() or out1 == out2
    assert len(list(shards_dir.glob("iclr-2025.*.json"))) == 1
