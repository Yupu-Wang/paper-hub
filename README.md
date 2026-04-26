# Paper Hub

> A static, zero-cost search engine for top ML conference papers.
>
> 顶会论文搜索网站 — 纯静态、零成本、客户端全文检索。

**Live site:** https://yupu-wang.github.io/paper-hub/

## What it does

Index every accepted paper from selected ML conferences and let you search them by keyword, author, conference, year, and presentation type — all in your browser, with no backend.

**Currently indexed:** 17,598 papers
- ICLR 2025 — 3,703 papers
- ICLR 2026 — 5,352 papers
- ICML 2025 — 3,257 papers
- NeurIPS 2025 — 5,286 papers

Each result links back to the paper's OpenReview page where you can read or download the PDF.

## Features

- **Full-text search** across title, abstract, authors, and keywords (powered by [MiniSearch](https://github.com/lucaong/minisearch))
- **Filters:** conference, year, author
- **Presentation tags:** oral / spotlight / poster (parsed from OpenReview venue field)
- **Incremental updates:** each `<conference>-<year>` is its own shard — adding a new conference only ships one new file, all existing shards stay browser-cached
- **Zero infrastructure:** static HTML/CSS/JS on GitHub Pages, no server, no database, no JS framework

## Architecture

```
[Python scrapers] → data/raw/<conf>-<year>.json     (one per conf+year)
       ↓ build
[Build scripts]   → data/shards/<conf>-<year>.<hash>.json
                    data/manifest.json
       ↓ git push
[GitHub Pages]    serves web/ + data/
       ↓
[Browser]         loads manifest, fetches shards in parallel,
                  builds in-memory MiniSearch index, runs queries
```

Full design rationale: [`docs/specs/2026-04-26-paper-hub-design.md`](docs/specs/2026-04-26-paper-hub-design.md)

## Local development

Requires Python 3.11+ and a Conda environment.

```bash
# One-time setup
conda create -n paper-hub python=3.11 -y
conda activate paper-hub
pip install -r scrapers/requirements.txt

# Run tests
make test

# Local preview (creates a symlink web/data → ../data)
make serve
# → open http://localhost:8000
```

## Adding a new conference / year

```bash
make update CONF=neurips YEAR=2026
git add data/ && git commit -m "Add NeurIPS 2026" && git push
```

GitHub Actions auto-deploys to Pages within a few minutes. Browser caches old shards via content-hash filenames, so users only download the new one.

**Currently supported sources:**
- ICLR / ICML / NeurIPS via OpenReview API (2023+ for ICML/NeurIPS)
- Older years (ICML 2021–2022, NeurIPS 2021–2022) require a separate scraper that hasn't been written yet — would target `proceedings.mlr.press` and `papers.nips.cc` respectively.

## Project structure

```
paper-hub/
├── scrapers/                # Python data pipeline
│   ├── fetch_iclr.py        #   one fetcher per conference
│   ├── fetch_icml.py
│   ├── fetch_neurips.py
│   ├── build_shard.py       #   raw → shard (with content-hash filename)
│   ├── build_manifest.py    #   regenerates manifest.json from shards/
│   └── common/
│       ├── schema.py        #   pydantic Paper model
│       └── openreview_client.py
├── data/
│   ├── raw/                 # source-of-truth, committed
│   ├── shards/              # served to frontend
│   └── manifest.json
├── web/                     # static site
│   ├── index.html
│   ├── main.js              #   loads shards + builds index
│   ├── search.js            #   query + filter
│   ├── render.js            #   result list + infinite scroll
│   └── styles.css
├── tests/                   # 42 pytest tests
└── docs/
    ├── specs/               # design docs
    └── plans/               # implementation plans
```

## Unified paper schema

Every paper, regardless of source, conforms to:

```json
{
  "id": "iclr-2025-1",
  "title": "...",
  "authors": ["...", "..."],
  "abstract": "...",
  "keywords": ["...", "..."],
  "conference": "ICLR",
  "year": 2025,
  "url": "https://openreview.net/forum?id=...",
  "presentation": "oral"
}
```

Validated by `scrapers/common/schema.py` — invalid entries are dropped with a warning during build.

## Future ideas (not implemented)

- AI-generated Chinese abstract translations
- AI one-line paper summaries
- Backfill 2021–2024 historical years
- Add security conferences (CCS / USENIX Security / S&P)
- Saved/favorites list (browser localStorage)
