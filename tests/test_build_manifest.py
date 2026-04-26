import json
from pathlib import Path
from scrapers.build_manifest import build_manifest


def test_build_manifest_lists_all_shards(tmp_path):
    shards = tmp_path / "shards"
    shards.mkdir()
    (shards / "iclr-2025.aaaaaa.json").write_text(json.dumps({
        "conference": "ICLR", "year": 2025, "count": 100,
        "built_at": "2026-04-26T15:00:00+08:00", "papers": [],
    }))
    (shards / "icml-2025.bbbbbb.json").write_text(json.dumps({
        "conference": "ICML", "year": 2025, "count": 200,
        "built_at": "2026-04-26T15:00:00+08:00", "papers": [],
    }))
    manifest_path = tmp_path / "manifest.json"
    build_manifest(shards, manifest_path)
    m = json.loads(manifest_path.read_text())
    assert "built_at" in m
    assert len(m["shards"]) == 2
    names = {s["file"] for s in m["shards"]}
    assert "shards/iclr-2025.aaaaaa.json" in names
    assert "shards/icml-2025.bbbbbb.json" in names
    for s in m["shards"]:
        assert {"conference", "year", "count", "file", "size_bytes"} <= s.keys()
