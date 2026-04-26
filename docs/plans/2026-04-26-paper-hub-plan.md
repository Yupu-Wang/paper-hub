# Paper Hub 实施计划

**日期：** 2026-04-26
**对应设计：** [2026-04-26-paper-hub-design.md](../specs/2026-04-26-paper-hub-design.md)
**目标：** 从零搭建 MVP，3 个 shard（ICLR / ICML / NeurIPS 2025）部署到 GitHub Pages。
**TDD 原则：** 每段功能性代码先写失败测试，再写最少实现。所有任务颗粒度 2-5 分钟。

---

## Phase 0：项目骨架

### 任务 0.1：初始化 Git 仓库 + 目录骨架

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/.gitignore`
- 新建：所有空目录

- [ ] 步骤 1：建目录结构
  ```bash
  cd /Users/yupuwang/Documents/code/paper-hub
  mkdir -p scrapers/common data/raw data/shards web/lib tests/fixtures .github/workflows docs/summary
  ```

- [ ] 步骤 2：写 `.gitignore`
  ```gitignore
  __pycache__/
  *.pyc
  .pytest_cache/
  .DS_Store
  .vscode/
  .idea/
  *.egg-info/
  .env
  # conda 环境本身不入库
  env/
  venv/
  ```

- [ ] 步骤 3：`git init` 并验证
  ```bash
  git init
  git status
  ```
  期望：列出 `.gitignore` 和 docs/。

- [ ] 步骤 4：Commit
  ```bash
  git add .gitignore docs/
  git commit -m "Initial project skeleton"
  ```

---

### 任务 0.2：创建 Conda 环境 + 依赖

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/requirements.txt`

- [ ] 步骤 1：创建 conda 环境
  ```bash
  conda create -n paper-hub python=3.11 -y
  conda activate paper-hub
  ```

- [ ] 步骤 2：写 `scrapers/requirements.txt`
  ```
  openreview-py>=1.40.0
  requests>=2.31.0
  beautifulsoup4>=4.12.0
  tqdm>=4.66.0
  pydantic>=2.0.0
  pytest>=7.4.0
  ```

- [ ] 步骤 3：安装依赖
  ```bash
  pip install -r scrapers/requirements.txt
  ```

- [ ] 步骤 4：验证安装
  ```bash
  python -c "import openreview, requests, bs4, tqdm, pydantic, pytest; print('OK')"
  ```
  期望输出：`OK`

- [ ] 步骤 5：Commit
  ```bash
  git add scrapers/requirements.txt
  git commit -m "Add Python dependencies"
  ```

---

### 任务 0.3：写 README + Python 包入口

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/README.md`
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/__init__.py`（空）
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/common/__init__.py`（空）

- [ ] 步骤 1：写 README.md（最小版本）
  ```markdown
  # Paper Hub

  顶会论文搜索网站。MVP：ICLR / ICML / NeurIPS 2025。

  设计：[docs/specs/2026-04-26-paper-hub-design.md](docs/specs/2026-04-26-paper-hub-design.md)
  计划：[docs/plans/2026-04-26-paper-hub-plan.md](docs/plans/2026-04-26-paper-hub-plan.md)

  ## 快速开始

  ```bash
  conda activate paper-hub
  make update CONF=iclr YEAR=2025
  make update CONF=icml YEAR=2025
  make update CONF=neurips YEAR=2025
  python -m http.server -d web 8000  # 本地预览
  ```
  ```

- [ ] 步骤 2：建空的 `__init__.py` 让 `scrapers` 成为包
  ```bash
  touch scrapers/__init__.py scrapers/common/__init__.py tests/__init__.py
  ```

- [ ] 步骤 3：Commit
  ```bash
  git add README.md scrapers/__init__.py scrapers/common/__init__.py tests/__init__.py
  git commit -m "Add README and package init files"
  ```

---

## Phase 1：Schema 与校验（TDD）

### 任务 1.1：写 schema 校验失败测试（合法论文应通过）

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/tests/test_schema.py`

- [ ] 步骤 1：写失败测试
  ```python
  # tests/test_schema.py
  import pytest
  from scrapers.common.schema import validate, Paper

  VALID_PAPER = {
      "id": "iclr-2025-1",
      "title": "Sample Paper",
      "authors": ["Alice"],
      "abstract": "An abstract.",
      "keywords": ["ml"],
      "conference": "ICLR",
      "year": 2025,
      "url": "https://openreview.net/forum?id=abc",
      "presentation": "oral",
  }

  def test_valid_paper_passes():
      validate(VALID_PAPER)  # should not raise
  ```

- [ ] 步骤 2：跑测试，确认它失败
  ```bash
  cd /Users/yupuwang/Documents/code/paper-hub
  pytest tests/test_schema.py -v
  ```
  期望：`ImportError: No module named 'scrapers.common.schema'`

---

### 任务 1.2：实现最小 schema.py 让测试通过

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/common/schema.py`

- [ ] 步骤 1：写最小实现
  ```python
  # scrapers/common/schema.py
  from typing import Literal
  from pydantic import BaseModel, Field, HttpUrl

  Conference = Literal["ICLR", "ICML", "NeurIPS"]
  Presentation = Literal["oral", "spotlight", "poster"]

  class Paper(BaseModel):
      id: str = Field(min_length=1)
      title: str = Field(min_length=1)
      authors: list[str]
      abstract: str
      keywords: list[str]
      conference: Conference
      year: int = Field(ge=2000, le=2100)
      url: str = Field(min_length=1)
      presentation: Presentation | None

  def validate(paper: dict) -> Paper:
      """Raise pydantic.ValidationError if invalid; return parsed Paper otherwise."""
      return Paper(**paper)
  ```

- [ ] 步骤 2：跑测试，确认通过
  ```bash
  pytest tests/test_schema.py -v
  ```
  期望：`1 passed`

---

### 任务 1.3：补全各种非法情况的测试

**涉及文件：**
- 修改：`tests/test_schema.py`

- [ ] 步骤 1：追加测试
  ```python
  # tests/test_schema.py 末尾追加
  from pydantic import ValidationError

  @pytest.mark.parametrize("missing_field", [
      "id", "title", "authors", "abstract", "keywords",
      "conference", "year", "url",
  ])
  def test_missing_required_field(missing_field):
      paper = {**VALID_PAPER}
      del paper[missing_field]
      with pytest.raises(ValidationError):
          validate(paper)

  def test_empty_title_rejected():
      paper = {**VALID_PAPER, "title": ""}
      with pytest.raises(ValidationError):
          validate(paper)

  def test_empty_id_rejected():
      paper = {**VALID_PAPER, "id": ""}
      with pytest.raises(ValidationError):
          validate(paper)

  def test_unknown_conference_rejected():
      paper = {**VALID_PAPER, "conference": "FOO"}
      with pytest.raises(ValidationError):
          validate(paper)

  def test_invalid_presentation_rejected():
      paper = {**VALID_PAPER, "presentation": "keynote"}
      with pytest.raises(ValidationError):
          validate(paper)

  def test_presentation_can_be_null():
      paper = {**VALID_PAPER, "presentation": None}
      validate(paper)  # ok

  def test_year_out_of_range_rejected():
      paper = {**VALID_PAPER, "year": 1900}
      with pytest.raises(ValidationError):
          validate(paper)

  def test_empty_keywords_allowed():
      paper = {**VALID_PAPER, "keywords": []}
      validate(paper)  # ok

  def test_empty_authors_rejected():
      paper = {**VALID_PAPER, "authors": []}
      with pytest.raises(ValidationError):
          validate(paper)
  ```

- [ ] 步骤 2：跑全部测试
  ```bash
  pytest tests/test_schema.py -v
  ```
  期望：除了 `test_empty_authors_rejected`，其余全过。`test_empty_authors_rejected` 失败，因为当前实现允许空 authors。

---

### 任务 1.4：补充 authors 非空约束

**涉及文件：**
- 修改：`scrapers/common/schema.py`

- [ ] 步骤 1：改字段定义
  ```python
  # 把 authors: list[str] 改成
  authors: list[str] = Field(min_length=1)
  ```

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_schema.py -v
  ```
  期望：全部通过。

- [ ] 步骤 3：Commit
  ```bash
  git add scrapers/common/schema.py tests/test_schema.py
  git commit -m "Add Paper schema with pydantic validation + tests"
  ```

---

## Phase 2：ICLR 抓取（TDD）

### 任务 2.1：写 OpenReview decision 解析器测试

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/tests/test_openreview_client.py`

- [ ] 步骤 1：写测试
  ```python
  # tests/test_openreview_client.py
  import pytest
  from scrapers.common.openreview_client import parse_presentation, is_accepted

  @pytest.mark.parametrize("decision,expected", [
      ("Accept (oral)", "oral"),
      ("Accept (Oral)", "oral"),
      ("Accept (spotlight)", "spotlight"),
      ("Accept (Spotlight)", "spotlight"),
      ("Accept (poster)", "poster"),
      ("Accept", "poster"),
      ("Reject", None),
      ("", None),
      (None, None),
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
  ```

- [ ] 步骤 2：跑测试，确认失败
  ```bash
  pytest tests/test_openreview_client.py -v
  ```
  期望：`ImportError: No module named 'scrapers.common.openreview_client'`

---

### 任务 2.2：实现 decision 解析器

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/common/openreview_client.py`

- [ ] 步骤 1：写最小实现
  ```python
  # scrapers/common/openreview_client.py
  from __future__ import annotations
  import re

  def is_accepted(decision: str | None) -> bool:
      if not decision:
          return False
      return decision.strip().lower().startswith("accept")

  def parse_presentation(decision: str | None) -> str | None:
      if not is_accepted(decision):
          return None
      d = decision.lower()
      if "oral" in d:
          return "oral"
      if "spotlight" in d:
          return "spotlight"
      return "poster"
  ```

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_openreview_client.py -v
  ```
  期望：全部通过。

---

### 任务 2.3：实现 OpenReview 抓取客户端（薄封装）

**涉及文件：**
- 修改：`scrapers/common/openreview_client.py`

- [ ] 步骤 1：追加 fetcher 函数
  ```python
  # scrapers/common/openreview_client.py 末尾追加
  import openreview
  from tqdm import tqdm
  from typing import Iterator

  def _client() -> openreview.api.OpenReviewClient:
      return openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")

  def fetch_venue_papers(venue_id: str) -> Iterator[dict]:
      """Yield raw OpenReview submission notes for a venue (e.g., 'ICLR.cc/2025/Conference').

      Filters to accepted papers using the venue's decision invitation.
      """
      client = _client()
      submissions = client.get_all_notes(content={"venueid": venue_id})
      for s in tqdm(submissions, desc=f"Fetching {venue_id}"):
          # OpenReview API v2: decision is in venue field of accepted papers
          venue = (s.content.get("venue") or {}).get("value", "")
          # Anything with 'Accept' / 'Oral' / 'Spotlight' / 'Poster' in venue is accepted
          if not venue or "reject" in venue.lower() or "withdraw" in venue.lower():
              continue
          yield {
              "forum_id": s.id,
              "title": (s.content.get("title") or {}).get("value", ""),
              "authors": (s.content.get("authors") or {}).get("value", []),
              "abstract": (s.content.get("abstract") or {}).get("value", ""),
              "keywords": (s.content.get("keywords") or {}).get("value", []),
              "decision": venue,
          }
  ```

  > 注意：OpenReview v2 API 把 decision 编码在 `venue` 字段里（如 `"ICLR 2025 Oral"`），不再是单独的 decision invitation。`parse_presentation` 仍然能用同一套关键字匹配。

- [ ] 步骤 2：手动验证（小规模真实调用）
  ```bash
  python -c "
  from scrapers.common.openreview_client import fetch_venue_papers
  papers = list(fetch_venue_papers('ICLR.cc/2025/Conference'))
  print(f'count={len(papers)}')
  print(papers[0] if papers else 'empty')
  "
  ```
  期望：count > 1000，第一条是 dict，含 title/authors/abstract。

- [ ] 步骤 3：Commit
  ```bash
  git add scrapers/common/openreview_client.py tests/test_openreview_client.py
  git commit -m "Add OpenReview client with decision parsing"
  ```

---

### 任务 2.4：写 fetch_iclr.py 入口脚本

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/fetch_iclr.py`

- [ ] 步骤 1：实现 fetcher
  ```python
  # scrapers/fetch_iclr.py
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

  def fetch(year: int) -> dict:
      venue_id = f"ICLR.cc/{year}/Conference"
      raw_papers = list(fetch_venue_papers(venue_id))
      papers = []
      for i, p in enumerate(raw_papers, start=1):
          paper = {
              "id": f"iclr-{year}-{i}",
              "title": p["title"].strip(),
              "authors": p["authors"],
              "abstract": p["abstract"].strip(),
              "keywords": p["keywords"],
              "conference": "ICLR",
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
          "conference": "ICLR",
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
      out = args.output or Path(f"data/raw/iclr-{args.year}.json")
      out.parent.mkdir(parents=True, exist_ok=True)
      out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
      print(f"Wrote {len(result['papers'])} papers to {out}")

  if __name__ == "__main__":
      main()
  ```

- [ ] 步骤 2：跑一次（真实抓取，几分钟）
  ```bash
  python -m scrapers.fetch_iclr --year 2025
  ```
  期望：`data/raw/iclr-2025.json` 生成，`Wrote N papers` 中 N > 1000。

- [ ] 步骤 3：抽查输出
  ```bash
  python -c "
  import json
  d = json.load(open('data/raw/iclr-2025.json'))
  print('count:', len(d['papers']))
  print('sample:', json.dumps(d['papers'][0], indent=2, ensure_ascii=False)[:500])
  "
  ```
  期望：第一篇论文字段齐全，title 非空，presentation 在 oral/spotlight/poster 中。

- [ ] 步骤 4：Commit
  ```bash
  git add scrapers/fetch_iclr.py data/raw/iclr-2025.json
  git commit -m "Add ICLR fetcher and ICLR 2025 raw data"
  ```

---

## Phase 3：ICML 抓取（TDD）

### 任务 3.1：保存 PMLR HTML fixture

- [ ] 步骤 1：手动找 ICML 2025 的 PMLR 卷号（如不确定，先用 2024 v235 验证流程）
  ```bash
  curl -s "https://proceedings.mlr.press/" | grep -i "icml" | head
  ```
  期望：能看到 ICML 各年的卷号列表，记下 2025 卷号（如 v267）。

- [ ] 步骤 2：保存索引页 fixture
  ```bash
  curl -s "https://proceedings.mlr.press/v235/" -o tests/fixtures/pmlr_volume_v235.html
  # 等 ICML 2025 卷号确认后再下载对应 fixture
  ```

- [ ] 步骤 3：从 fixture 中找一篇论文详情页 URL，下载
  ```bash
  # 详情页 URL 形如 https://proceedings.mlr.press/v235/abc24a.html
  curl -s "<paper_detail_url>" -o tests/fixtures/pmlr_paper_sample.html
  ```

- [ ] 步骤 4：暂存 fixture（不 commit 到 git，加 .gitignore 排除大 HTML）
  ```bash
  echo "tests/fixtures/*.html" >> .gitignore
  ```

---

### 任务 3.2：写 PMLR 解析器测试

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/tests/test_pmlr.py`

- [ ] 步骤 1：写测试（基于 fixture）
  ```python
  # tests/test_pmlr.py
  from pathlib import Path
  from scrapers.common.pmlr import parse_volume_index, parse_paper_page

  FIXTURES = Path(__file__).parent / "fixtures"

  def test_parse_volume_index_returns_paper_links():
      html = (FIXTURES / "pmlr_volume_v235.html").read_text()
      links = parse_volume_index(html, base_url="https://proceedings.mlr.press/v235/")
      assert len(links) > 100  # ICML 2024 had ~2600 papers
      assert all(link.startswith("https://proceedings.mlr.press/v235/") for link in links)
      assert all(link.endswith(".html") for link in links)

  def test_parse_paper_page_extracts_metadata():
      html = (FIXTURES / "pmlr_paper_sample.html").read_text()
      meta = parse_paper_page(html)
      assert meta["title"]
      assert isinstance(meta["authors"], list) and len(meta["authors"]) >= 1
      assert isinstance(meta["abstract"], str) and len(meta["abstract"]) > 50
  ```

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_pmlr.py -v
  ```
  期望：`ImportError: No module named 'scrapers.common.pmlr'`

---

### 任务 3.3：实现 PMLR 解析器

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/common/pmlr.py`

- [ ] 步骤 1：实现解析函数
  ```python
  # scrapers/common/pmlr.py
  from __future__ import annotations
  from urllib.parse import urljoin
  from bs4 import BeautifulSoup

  def parse_volume_index(html: str, base_url: str) -> list[str]:
      """Return absolute URLs of all paper detail pages from a PMLR volume index."""
      soup = BeautifulSoup(html, "html.parser")
      # Each paper is a div.paper with a link in .title > a
      links = []
      for div in soup.select("div.paper p.links a"):
          href = div.get("href", "")
          if href.endswith(".html"):
              links.append(urljoin(base_url, href))
      # Deduplicate while preserving order
      seen = set()
      unique = []
      for link in links:
          if link not in seen:
              seen.add(link)
              unique.append(link)
      return unique

  def parse_paper_page(html: str) -> dict:
      """Extract title, authors, abstract from a PMLR paper detail page."""
      soup = BeautifulSoup(html, "html.parser")
      title = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else ""
      authors_text = soup.select_one("#authors").get_text(strip=True) if soup.select_one("#authors") else ""
      authors = [a.strip() for a in authors_text.split(",") if a.strip()]
      abstract_el = soup.select_one("#abstract") or soup.select_one(".abstract")
      abstract = abstract_el.get_text(strip=True) if abstract_el else ""
      return {"title": title, "authors": authors, "abstract": abstract}
  ```

  > 注意：PMLR HTML 结构以 fixture 为准；如果选择器对不上，跑测试时会失败，逐个调整选择器即可。

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_pmlr.py -v
  ```
  期望：通过。如果失败，根据 fixture 实际结构调整 CSS 选择器。

- [ ] 步骤 3：Commit
  ```bash
  git add scrapers/common/pmlr.py tests/test_pmlr.py .gitignore
  git commit -m "Add PMLR HTML parser"
  ```

---

### 任务 3.4：写 fetch_icml.py

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/fetch_icml.py`

- [ ] 步骤 1：实现
  ```python
  # scrapers/fetch_icml.py
  from __future__ import annotations
  import argparse
  import json
  import logging
  import time
  from datetime import datetime, timezone, timedelta
  from pathlib import Path

  import requests
  from tqdm import tqdm

  from scrapers.common.pmlr import parse_volume_index, parse_paper_page
  from scrapers.common.schema import validate

  log = logging.getLogger(__name__)
  CST = timezone(timedelta(hours=8))

  ICML_VOLUMES = {
      2021: "v139",
      2022: "v162",
      2023: "v202",
      2024: "v235",
      2025: None,  # 抓取时通过 --volume 传入，或先在 PMLR 站点查到后填回这里
  }

  def get(url: str, max_retries: int = 3) -> str:
      for attempt in range(max_retries):
          try:
              r = requests.get(url, timeout=30)
              r.raise_for_status()
              return r.text
          except Exception as e:
              if attempt == max_retries - 1:
                  raise
              wait = 2 ** attempt
              log.warning("retry %s in %ds: %s", url, wait, e)
              time.sleep(wait)
      raise RuntimeError("unreachable")

  def fetch(year: int, volume: str | None) -> dict:
      vol = volume or ICML_VOLUMES.get(year)
      if not vol:
          raise SystemExit(f"Unknown ICML volume for year {year}; pass --volume vXXX")
      base = f"https://proceedings.mlr.press/{vol}/"
      index_html = get(base)
      paper_urls = parse_volume_index(index_html, base)
      log.info("found %d papers in %s", len(paper_urls), vol)

      papers = []
      for i, url in enumerate(tqdm(paper_urls, desc=f"ICML {year}"), start=1):
          try:
              meta = parse_paper_page(get(url))
              paper = {
                  "id": f"icml-{year}-{i}",
                  "title": meta["title"],
                  "authors": meta["authors"],
                  "abstract": meta["abstract"],
                  "keywords": [],
                  "conference": "ICML",
                  "year": year,
                  "url": url,
                  "presentation": None,
              }
              validate(paper)
              papers.append(paper)
          except Exception as e:
              log.warning("skip %s: %s", url, e)

      return {
          "conference": "ICML",
          "year": year,
          "fetched_at": datetime.now(CST).isoformat(timespec="seconds"),
          "source": f"pmlr/{vol}",
          "papers": papers,
      }

  def main() -> None:
      logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
      ap = argparse.ArgumentParser()
      ap.add_argument("--year", type=int, required=True)
      ap.add_argument("--volume", default=None, help="PMLR volume id, e.g., v267")
      ap.add_argument("--output", type=Path, default=None)
      args = ap.parse_args()

      result = fetch(args.year, args.volume)
      out = args.output or Path(f"data/raw/icml-{args.year}.json")
      out.parent.mkdir(parents=True, exist_ok=True)
      out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
      print(f"Wrote {len(result['papers'])} papers to {out}")

  if __name__ == "__main__":
      main()
  ```

- [ ] 步骤 2：跑（如果 ICML 2025 卷号未填，临时跑 2024 v235 验证流程）
  ```bash
  python -m scrapers.fetch_icml --year 2024
  # 或 ICML 2025 已查到：
  # python -m scrapers.fetch_icml --year 2025 --volume v267
  ```
  期望：完整跑完，`Wrote N papers to data/raw/icml-2025.json`，N > 1000。

- [ ] 步骤 3：抽查
  ```bash
  python -c "
  import json
  d = json.load(open('data/raw/icml-2025.json'))
  print('count:', len(d['papers']))
  print('sample title:', d['papers'][0]['title'])
  "
  ```

- [ ] 步骤 4：Commit
  ```bash
  git add scrapers/fetch_icml.py data/raw/icml-2025.json
  git commit -m "Add ICML fetcher and ICML 2025 raw data"
  ```

---

## Phase 4：NeurIPS 抓取（TDD）

### 任务 4.1：保存 papers.nips.cc fixture

- [ ] 步骤 1：下载索引页 + 详情页
  ```bash
  curl -s "https://papers.nips.cc/paper_files/paper/2022" -o tests/fixtures/nips_index_2022.html
  # 从索引页里挑一个详情页 URL 下载
  curl -s "<a paper detail url>" -o tests/fixtures/nips_paper_2022.html
  ```

---

### 任务 4.2：写 papers.nips.cc 解析器测试

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/tests/test_neurips_legacy.py`

- [ ] 步骤 1：写测试
  ```python
  # tests/test_neurips_legacy.py
  from pathlib import Path
  from scrapers.common.neurips_legacy import parse_index, parse_paper_page

  FIXTURES = Path(__file__).parent / "fixtures"

  def test_parse_index():
      html = (FIXTURES / "nips_index_2022.html").read_text()
      links = parse_index(html, base_url="https://papers.nips.cc")
      assert len(links) > 1000
      assert all(link.startswith("https://papers.nips.cc/paper_files/paper/") for link in links)

  def test_parse_paper_page():
      html = (FIXTURES / "nips_paper_2022.html").read_text()
      meta = parse_paper_page(html)
      assert meta["title"]
      assert isinstance(meta["authors"], list) and len(meta["authors"]) >= 1
      assert len(meta["abstract"]) > 50
  ```

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_neurips_legacy.py -v
  ```
  期望：失败（模块不存在）。

---

### 任务 4.3：实现 papers.nips.cc 解析器

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/common/neurips_legacy.py`

- [ ] 步骤 1：写实现
  ```python
  # scrapers/common/neurips_legacy.py
  from __future__ import annotations
  from urllib.parse import urljoin
  from bs4 import BeautifulSoup

  def parse_index(html: str, base_url: str) -> list[str]:
      """Return paper detail URLs from a papers.nips.cc year index page."""
      soup = BeautifulSoup(html, "html.parser")
      links = []
      for a in soup.select("a"):
          href = a.get("href", "")
          if "/paper_files/paper/" in href and "/hash/" in href:
              links.append(urljoin(base_url, href))
      seen = set()
      unique = [x for x in links if not (x in seen or seen.add(x))]
      return unique

  def parse_paper_page(html: str) -> dict:
      soup = BeautifulSoup(html, "html.parser")
      title_el = soup.select_one("h4") or soup.select_one("h1")
      title = title_el.get_text(strip=True) if title_el else ""
      # Authors usually after title in an <i> or .authors
      authors_el = soup.select_one(".authors") or soup.select_one("h4 + p i")
      authors_text = authors_el.get_text(strip=True) if authors_el else ""
      authors = [a.strip() for a in authors_text.split(",") if a.strip()]
      # Abstract: next <p> after the heading "Abstract"
      abstract = ""
      for h in soup.find_all(["h4", "h3", "h5"]):
          if "abstract" in h.get_text(strip=True).lower():
              p = h.find_next("p")
              if p:
                  abstract = p.get_text(strip=True)
              break
      return {"title": title, "authors": authors, "abstract": abstract}
  ```

  > 注：选择器以实际 fixture 为准，跑测试时调整。

- [ ] 步骤 2：跑测试，调整直到通过
  ```bash
  pytest tests/test_neurips_legacy.py -v
  ```

- [ ] 步骤 3：Commit
  ```bash
  git add scrapers/common/neurips_legacy.py tests/test_neurips_legacy.py
  git commit -m "Add papers.nips.cc parser"
  ```

---

### 任务 4.4：写 fetch_neurips.py（年份分支）

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/fetch_neurips.py`

- [ ] 步骤 1：实现
  ```python
  # scrapers/fetch_neurips.py
  from __future__ import annotations
  import argparse
  import json
  import logging
  import time
  from datetime import datetime, timezone, timedelta
  from pathlib import Path

  import requests
  from tqdm import tqdm

  from scrapers.common.openreview_client import fetch_venue_papers, parse_presentation
  from scrapers.common.neurips_legacy import parse_index, parse_paper_page
  from scrapers.common.schema import validate

  log = logging.getLogger(__name__)
  CST = timezone(timedelta(hours=8))

  def fetch_via_openreview(year: int) -> list[dict]:
      venue_id = f"NeurIPS.cc/{year}/Conference"
      papers = []
      for i, p in enumerate(fetch_venue_papers(venue_id), start=1):
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
              log.warning("skip %s: %s", paper["id"], e)
      return papers

  def get(url: str, retries: int = 3) -> str:
      for i in range(retries):
          try:
              r = requests.get(url, timeout=30)
              r.raise_for_status()
              return r.text
          except Exception as e:
              if i == retries - 1: raise
              time.sleep(2 ** i)
      raise RuntimeError("unreachable")

  def fetch_via_legacy(year: int) -> list[dict]:
      base = "https://papers.nips.cc"
      index_html = get(f"{base}/paper_files/paper/{year}")
      links = parse_index(index_html, base)
      papers = []
      for i, url in enumerate(tqdm(links, desc=f"NeurIPS {year}"), start=1):
          try:
              meta = parse_paper_page(get(url))
              paper = {
                  "id": f"neurips-{year}-{i}",
                  "title": meta["title"],
                  "authors": meta["authors"],
                  "abstract": meta["abstract"],
                  "keywords": [],
                  "conference": "NeurIPS",
                  "year": year,
                  "url": url,
                  "presentation": None,
              }
              validate(paper)
              papers.append(paper)
          except Exception as e:
              log.warning("skip %s: %s", url, e)
      return papers

  def fetch(year: int) -> dict:
      if year >= 2023:
          source = "openreview"
          papers = fetch_via_openreview(year)
      else:
          source = "papers.nips.cc"
          papers = fetch_via_legacy(year)
      return {
          "conference": "NeurIPS",
          "year": year,
          "fetched_at": datetime.now(CST).isoformat(timespec="seconds"),
          "source": source,
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
  ```

- [ ] 步骤 2：跑 NeurIPS 2025（OpenReview 分支）
  ```bash
  python -m scrapers.fetch_neurips --year 2025
  ```
  期望：完整跑完。如果 NeurIPS 2025 还没在 OpenReview 上线，先跑 2023 验证流程；2025 数据等录取出来后再补。

- [ ] 步骤 3：抽查
  ```bash
  python -c "
  import json
  d = json.load(open('data/raw/neurips-2025.json'))
  print('count:', len(d['papers']))
  "
  ```

- [ ] 步骤 4：Commit
  ```bash
  git add scrapers/fetch_neurips.py data/raw/neurips-2025.json
  git commit -m "Add NeurIPS fetcher (year-branched) and NeurIPS 2025 raw data"
  ```

---

## Phase 5：构建 shard + manifest + Makefile

### 任务 5.1：写 build_shard 测试

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/tests/test_build_shard.py`

- [ ] 步骤 1：写测试
  ```python
  # tests/test_build_shard.py
  import json
  from pathlib import Path
  from scrapers.build_shard import build, content_hash

  def test_content_hash_stable(tmp_path):
      data = {"a": 1, "b": [1, 2, 3]}
      h1 = content_hash(data)
      h2 = content_hash(data)
      assert h1 == h2
      assert len(h1) == 6  # short hash
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
          "papers": [{"id": "bad", "title": ""}],  # missing fields, empty title
      }
      raw_path = tmp_path / "iclr-2025.json"
      raw_path.write_text(json.dumps(raw))
      shards_dir = tmp_path / "shards"
      out = build(raw_path, shards_dir)
      shard = json.loads(out.read_text())
      assert shard["count"] == 0  # invalid paper dropped
  ```

- [ ] 步骤 2：跑测试，确认失败
  ```bash
  pytest tests/test_build_shard.py -v
  ```
  期望：`ImportError`.

---

### 任务 5.2：实现 build_shard.py

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/scrapers/build_shard.py`

- [ ] 步骤 1：写实现
  ```python
  # scrapers/build_shard.py
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

  def content_hash(data: dict) -> str:
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
      shard = {
          "conference": raw["conference"],
          "year": year,
          "count": len(papers),
          "built_at": datetime.now(CST).isoformat(timespec="seconds"),
          "papers": papers,
      }
      h = content_hash({"papers": papers})  # hash only papers (built_at would change on every run)
      shards_dir.mkdir(parents=True, exist_ok=True)
      out = shards_dir / f"{conf}-{year}.{h}.json"
      # Remove older versions of same conf-year
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
  ```

- [ ] 步骤 2：跑测试
  ```bash
  pytest tests/test_build_shard.py -v
  ```
  期望：通过。

---

### 任务 5.3：写 build_manifest 测试 + 实现

**涉及文件：**
- 新建：`tests/test_build_manifest.py`
- 新建：`scrapers/build_manifest.py`

- [ ] 步骤 1：写测试
  ```python
  # tests/test_build_manifest.py
  import json
  from pathlib import Path
  from scrapers.build_manifest import build_manifest

  def test_build_manifest_lists_all_shards(tmp_path):
      shards = tmp_path / "shards"
      shards.mkdir()
      (shards / "iclr-2025.aaaaaa.json").write_text(json.dumps({
          "conference": "ICLR", "year": 2025, "count": 100,
          "built_at": "2026-04-26T15:00:00+08:00", "papers": []
      }))
      (shards / "icml-2025.bbbbbb.json").write_text(json.dumps({
          "conference": "ICML", "year": 2025, "count": 200,
          "built_at": "2026-04-26T15:00:00+08:00", "papers": []
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
  ```

- [ ] 步骤 2：跑测试，确认失败
  ```bash
  pytest tests/test_build_manifest.py -v
  ```

- [ ] 步骤 3：实现
  ```python
  # scrapers/build_manifest.py
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
  ```

- [ ] 步骤 4：跑测试，确认通过
  ```bash
  pytest tests/test_build_manifest.py -v
  ```

- [ ] 步骤 5：Commit
  ```bash
  git add scrapers/build_shard.py scrapers/build_manifest.py tests/test_build_shard.py tests/test_build_manifest.py
  git commit -m "Add build_shard and build_manifest with tests"
  ```

---

### 任务 5.4：写 Makefile

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/Makefile`

- [ ] 步骤 1：写 Makefile
  ```makefile
  .PHONY: update build-shard build-manifest test serve

  update:
  	python -m scrapers.fetch_$(CONF) --year $(YEAR)
  	python -m scrapers.build_shard --conf $(CONF) --year $(YEAR)
  	python -m scrapers.build_manifest

  build-shard:
  	python -m scrapers.build_shard --conf $(CONF) --year $(YEAR)

  build-manifest:
  	python -m scrapers.build_manifest

  test:
  	pytest tests/ -v

  serve:
  	@echo "Visit http://localhost:8000"
  	cd web && python -m http.server 8000
  ```

- [ ] 步骤 2：跑一次完整流程验证（用已抓的 ICLR 2025 数据）
  ```bash
  make build-shard CONF=iclr YEAR=2025
  make build-manifest
  ls data/shards/
  cat data/manifest.json
  ```
  期望：看到 `iclr-2025.<hash>.json`，manifest 列出 1 个 shard。

- [ ] 步骤 3：Commit
  ```bash
  git add Makefile
  git commit -m "Add Makefile"
  ```

---

## Phase 6：前端

### 任务 6.1：HTML 骨架

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/web/index.html`

- [ ] 步骤 1：写 HTML
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>Paper Hub</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <header>
      <h1>Paper Hub</h1>
      <div id="progress">加载中…</div>
    </header>
    <main>
      <aside id="sidebar">
        <input id="search" type="search" placeholder="关键词搜索" autofocus />
        <fieldset>
          <legend>会议</legend>
          <label><input type="checkbox" name="conf" value="ICLR" checked> ICLR</label>
          <label><input type="checkbox" name="conf" value="ICML" checked> ICML</label>
          <label><input type="checkbox" name="conf" value="NeurIPS" checked> NeurIPS</label>
        </fieldset>
        <fieldset id="year-filter"><legend>年份</legend></fieldset>
        <fieldset>
          <legend>排序</legend>
          <select id="sort">
            <option value="relevance">相关度</option>
            <option value="year-desc">年份新→旧</option>
          </select>
        </fieldset>
        <input id="author-search" type="search" placeholder="作者名" />
      </aside>
      <section id="results">
        <p class="hint">输入关键词或选择筛选条件</p>
      </section>
    </main>
    <script src="lib/minisearch.min.js"></script>
    <script type="module" src="main.js"></script>
  </body>
  </html>
  ```

---

### 任务 6.2：放入 MiniSearch 库

- [ ] 步骤 1：下载 MiniSearch UMD 构建
  ```bash
  curl -L "https://cdn.jsdelivr.net/npm/minisearch@7.1.0/dist/umd/index.min.js" -o web/lib/minisearch.min.js
  ```

- [ ] 步骤 2：验证文件大小（应在 ~30KB）
  ```bash
  ls -la web/lib/minisearch.min.js
  ```

---

### 任务 6.3：实现 main.js（加载 + 索引构建）

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/web/main.js`

- [ ] 步骤 1：写主入口
  ```javascript
  // web/main.js
  import { renderResults } from "./render.js";
  import { runSearch } from "./search.js";

  const state = {
      papers: [],          // all loaded papers
      index: null,         // MiniSearch instance
      shardsTotal: 0,
      shardsLoaded: 0,
  };

  const progress = document.getElementById("progress");
  const resultsEl = document.getElementById("results");
  const yearFilter = document.getElementById("year-filter");

  function setProgress() {
      if (state.shardsLoaded < state.shardsTotal) {
          progress.textContent = `加载中… ${state.shardsLoaded}/${state.shardsTotal}`;
      } else {
          progress.textContent = `已加载 ${state.papers.length} 篇`;
      }
  }

  function ensureIndex() {
      if (!state.index) {
          state.index = new MiniSearch({
              fields: ["title", "abstract", "authors_text", "keywords_text"],
              storeFields: ["id", "title", "authors", "abstract", "conference", "year", "url", "presentation"],
              searchOptions: { boost: { title: 2, keywords_text: 1.5 }, prefix: true },
          });
      }
  }

  function indexPapers(papers) {
      ensureIndex();
      const docs = papers.map(p => ({
          ...p,
          authors_text: p.authors.join(" "),
          keywords_text: (p.keywords || []).join(" "),
      }));
      state.index.addAll(docs);
  }

  function rebuildYearFilter() {
      const years = [...new Set(state.papers.map(p => p.year))].sort((a, b) => b - a);
      yearFilter.innerHTML = "<legend>年份</legend>" + years.map(y =>
          `<label><input type="checkbox" name="year" value="${y}" checked> ${y}</label>`
      ).join("");
      attachFilterListeners();
  }

  async function loadShards() {
      const manifest = await fetch("../data/manifest.json").then(r => r.json());
      state.shardsTotal = manifest.shards.length;
      setProgress();
      await Promise.all(manifest.shards.map(async (s) => {
          const data = await fetch(`../data/${s.file}`).then(r => r.json());
          state.papers.push(...data.papers);
          indexPapers(data.papers);
          state.shardsLoaded += 1;
          setProgress();
          rebuildYearFilter();
          triggerSearch();
      }));
  }

  function triggerSearch() {
      const q = document.getElementById("search").value.trim();
      const author = document.getElementById("author-search").value.trim();
      const confs = [...document.querySelectorAll("input[name=conf]:checked")].map(i => i.value);
      const years = [...document.querySelectorAll("input[name=year]:checked")].map(i => +i.value);
      const sort = document.getElementById("sort").value;
      const hits = runSearch(state, { q, author, confs, years, sort });
      renderResults(resultsEl, hits, q);
  }

  function attachFilterListeners() {
      document.querySelectorAll("input[name=conf], input[name=year]").forEach(i =>
          i.addEventListener("change", triggerSearch)
      );
  }

  let debounce;
  document.getElementById("search").addEventListener("input", () => {
      clearTimeout(debounce);
      debounce = setTimeout(triggerSearch, 200);
  });
  document.getElementById("author-search").addEventListener("input", () => {
      clearTimeout(debounce);
      debounce = setTimeout(triggerSearch, 200);
  });
  document.getElementById("sort").addEventListener("change", triggerSearch);
  attachFilterListeners();

  loadShards();
  ```

  > 注意：路径 `../data/manifest.json` 是因为 GitHub Pages 部署时 `/web` 是站点根；本地 `python -m http.server -d web 8000` 也类似。如果发现路径问题，部署阶段会调整成 `/data/...`。

---

### 任务 6.4：实现 search.js

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/web/search.js`

- [ ] 步骤 1：写搜索函数
  ```javascript
  // web/search.js
  export function runSearch(state, opts) {
      const { q, author, confs, years, sort } = opts;
      if (!q && !author && confs.length === 3 && years.length === state.shardsLoaded) {
          // No real filter: don't show all papers (would be 6000+ items)
          return null;
      }
      let candidates;
      if (q && state.index) {
          candidates = state.index.search(q, { combineWith: "AND" });
      } else {
          candidates = state.papers.map(p => ({ ...p, score: 0 }));
      }
      let filtered = candidates.filter(p =>
          confs.includes(p.conference) &&
          years.includes(p.year) &&
          (!author || p.authors.some(a => a.toLowerCase().includes(author.toLowerCase())))
      );
      if (sort === "year-desc") {
          filtered.sort((a, b) => b.year - a.year);
      }
      return filtered;
  }
  ```

---

### 任务 6.5：实现 render.js（结果渲染 + 无限滚动）

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/web/render.js`

- [ ] 步骤 1：写渲染
  ```javascript
  // web/render.js
  const PAGE_SIZE = 50;
  let currentHits = [];
  let renderedCount = 0;
  let observer;

  export function renderResults(container, hits, query) {
      container.innerHTML = "";
      currentHits = hits;
      renderedCount = 0;
      if (hits === null) {
          container.innerHTML = '<p class="hint">输入关键词或选择筛选条件</p>';
          return;
      }
      if (hits.length === 0) {
          container.innerHTML = `<p class="hint">没有匹配结果（共加载 ${currentHits.length} 篇）</p>`;
          return;
      }
      container.innerHTML = `<p class="meta">共 ${hits.length} 条结果</p><ul id="paper-list"></ul><div id="sentinel"></div>`;
      renderMore(container);
      attachInfiniteScroll(container);
  }

  function renderMore(container) {
      const list = container.querySelector("#paper-list");
      const slice = currentHits.slice(renderedCount, renderedCount + PAGE_SIZE);
      for (const p of slice) {
          list.appendChild(renderItem(p));
      }
      renderedCount += slice.length;
  }

  function renderItem(p) {
      const li = document.createElement("li");
      const tag = p.presentation ? ` · ${p.presentation}` : "";
      const preview = (p.abstract || "").slice(0, 200) + (p.abstract.length > 200 ? "…" : "");
      li.innerHTML = `
          <a href="${p.url}" target="_blank" rel="noopener">
              <div class="title">${escapeHtml(p.title)}</div>
              <div class="meta">${p.conference} ${p.year}${tag}</div>
              <div class="authors">${escapeHtml(p.authors.join(", "))}</div>
              <div class="abstract">${escapeHtml(preview)}</div>
          </a>
      `;
      return li;
  }

  function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({
          "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }[c]));
  }

  function attachInfiniteScroll(container) {
      if (observer) observer.disconnect();
      const sentinel = container.querySelector("#sentinel");
      if (!sentinel) return;
      observer = new IntersectionObserver(entries => {
          if (entries[0].isIntersecting && renderedCount < currentHits.length) {
              renderMore(container);
          }
      });
      observer.observe(sentinel);
  }
  ```

---

### 任务 6.6：写 styles.css

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/web/styles.css`

- [ ] 步骤 1：写样式
  ```css
  /* web/styles.css */
  * { box-sizing: border-box; }
  body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #222;
      background: #fafafa;
  }
  header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 20px; background: #1a1a2e; color: white;
  }
  header h1 { margin: 0; font-size: 20px; }
  #progress { font-size: 13px; opacity: 0.8; }
  main { display: flex; min-height: calc(100vh - 56px); }
  #sidebar {
      width: 260px; padding: 16px; background: white; border-right: 1px solid #e0e0e0;
      display: flex; flex-direction: column; gap: 14px;
  }
  #sidebar input[type=search], #sidebar select {
      width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;
  }
  fieldset { border: 1px solid #e0e0e0; border-radius: 4px; padding: 8px 12px; }
  fieldset label { display: block; font-size: 14px; padding: 2px 0; cursor: pointer; }
  #results { flex: 1; padding: 16px 24px; overflow-y: auto; }
  #results ul { list-style: none; padding: 0; margin: 0; }
  #results li { margin-bottom: 12px; }
  #results li a {
      display: block; padding: 14px 16px; background: white;
      border: 1px solid #e0e0e0; border-radius: 6px;
      color: inherit; text-decoration: none;
  }
  #results li a:hover { border-color: #4a90e2; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
  .title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
  .meta { color: #888; font-size: 13px; }
  .authors { color: #555; font-size: 13px; margin: 4px 0; }
  .abstract { font-size: 13px; color: #444; line-height: 1.5; }
  .hint { color: #888; padding: 24px 0; text-align: center; }
  ```

---

### 任务 6.7：本地启动并手动测试

- [ ] 步骤 1：启动 server
  ```bash
  cd /Users/yupuwang/Documents/code/paper-hub
  python -m http.server -d web 8000 &
  ```

- [ ] 步骤 2：访问 http://localhost:8000

- [ ] 步骤 3：手动验证清单
  - [ ] 进度条显示 `加载中… 0/N`，几秒后变 `已加载 X 篇`
  - [ ] 输入 "transformer" → 出现结果
  - [ ] 取消勾选 ICLR → 结果只剩 ICML/NeurIPS
  - [ ] 切换排序 → 顺序变化
  - [ ] 滚动到底部 → 自动加载下一页
  - [ ] 点击某条 → 新窗口打开 OpenReview/PMLR 页面
  - [ ] 输入作者名 → 结果按作者过滤

- [ ] 步骤 4：停止 server
  ```bash
  kill %1
  ```

- [ ] 步骤 5：Commit
  ```bash
  git add web/
  git commit -m "Add frontend: HTML/CSS/JS with MiniSearch client-side search"
  ```

---

## Phase 7：GitHub Pages 部署

### 任务 7.1：创建 GitHub 远程仓库

- [ ] 步骤 1：用 gh 创建仓库（私有；如果想公开改 `--public`）
  ```bash
  cd /Users/yupuwang/Documents/code/paper-hub
  gh repo create paper-hub --private --source=. --remote=origin --push
  ```
  期望：仓库创建成功，main 分支推送。

---

### 任务 7.2：写 GitHub Actions 部署工作流

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/.github/workflows/pages.yml`

- [ ] 步骤 1：写 workflow
  ```yaml
  # .github/workflows/pages.yml
  name: Deploy to GitHub Pages
  on:
    push:
      branches: [main]
      paths:
        - "web/**"
        - "data/manifest.json"
        - "data/shards/**"
        - ".github/workflows/pages.yml"
    workflow_dispatch:

  permissions:
    contents: read
    pages: write
    id-token: write

  concurrency:
    group: "pages"
    cancel-in-progress: false

  jobs:
    deploy:
      runs-on: ubuntu-latest
      environment:
        name: github-pages
        url: ${{ steps.deployment.outputs.page_url }}
      steps:
        - uses: actions/checkout@v4
        - name: Prepare site
          run: |
            mkdir -p _site
            cp -r web/* _site/
            mkdir -p _site/data/shards
            cp data/manifest.json _site/data/
            cp data/shards/*.json _site/data/shards/
        - uses: actions/configure-pages@v4
        - uses: actions/upload-pages-artifact@v3
          with:
            path: _site
        - id: deployment
          uses: actions/deploy-pages@v4
  ```

  > 关键改动：把 `web/` 复制到 `_site/`，并把 `data/` 拷到 `_site/data/`。这样部署后访问根路径就直接是 `index.html`，且 `fetch("data/manifest.json")` 工作。
  >
  > 此外需要**修改前端代码**，把 `../data/...` 改成 `data/...`（相对路径）。

- [ ] 步骤 2：修改 `web/main.js` 中的 fetch 路径
  ```javascript
  // 把 await fetch("../data/manifest.json")
  // 改成 await fetch("data/manifest.json")
  // 同样地 await fetch(`../data/${s.file}`) → await fetch(`data/${s.file}`)
  ```
  并相应调整 `make serve` 的本地路径方案：把 `web/` 下临时建符号链接 `data -> ../data`，或改成在仓库根起 server。简单点：改 Makefile：
  ```makefile
  serve:
  	@echo "Visit http://localhost:8000/web/"
  	python -m http.server 8000
  ```
  并在前端用 `data/manifest.json`（相对当前页面 `web/index.html`，会指向 `web/data/...`，所以要建符号链接）。
  **更简单方案**：在仓库根放一个 `index.html` 重定向到 `web/`，或者直接把站点根设为仓库根。最干净的做法是：
  - 部署时拷贝结构保持 `_site/{index.html, ..., data/}`
  - 本地预览时也保持同样结构：用一个 `make serve` 命令把 `data/` 临时挂到 `web/data/`

  ```makefile
  serve:
  	@ln -sfn ../data web/data
  	@echo "Visit http://localhost:8000"
  	cd web && python -m http.server 8000
  ```

  本地用相对路径 `data/manifest.json` → 访问 `web/data/manifest.json` → 通过软链接命中实际数据。部署后 `_site/data/manifest.json` 也工作。

- [ ] 步骤 3：commit
  ```bash
  git add .github/workflows/pages.yml web/main.js Makefile
  git commit -m "Add GitHub Pages deploy workflow and fix asset paths"
  ```

---

### 任务 7.3：在 GitHub 仓库启用 Pages

- [ ] 步骤 1：用 gh 命令启用 Pages（来源：GitHub Actions）
  ```bash
  gh api -X PUT /repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pages \
      -f build_type=workflow
  ```
  如果报"已存在"则忽略。

- [ ] 步骤 2：推送触发部署
  ```bash
  git push
  ```

- [ ] 步骤 3：观察部署状态
  ```bash
  gh run watch
  ```
  期望：Action 跑成功，最后输出 Pages URL。

- [ ] 步骤 4：访问 Pages URL，重复任务 6.7 步骤 3 的手动验证清单

---

## Phase 8：跑完整 MVP 数据 + 验收

### 任务 8.1：抓 ICML 2025 + NeurIPS 2025 真实数据

- [ ] 步骤 1：确认 ICML 2025 PMLR 卷号（如尚未在 ICML_VOLUMES 里写死）
  ```bash
  curl -s "https://proceedings.mlr.press/" | grep -oE "v[0-9]+/" | sort -u | tail -10
  ```
  找到 ICML 2025 的卷号，编辑 `scrapers/fetch_icml.py` 的 `ICML_VOLUMES` 字典补上。

- [ ] 步骤 2：跑 ICML 2025
  ```bash
  make update CONF=icml YEAR=2025
  ```

- [ ] 步骤 3：确认 NeurIPS 2025 是否在 OpenReview 上线
  ```bash
  python -c "
  from scrapers.common.openreview_client import fetch_venue_papers
  count = sum(1 for _ in fetch_venue_papers('NeurIPS.cc/2025/Conference'))
  print('NeurIPS 2025 papers:', count)
  "
  ```
  如果 count > 0：直接跑。如果为 0：先跑 NeurIPS 2024 占位，2025 出榜后再补。

- [ ] 步骤 4：跑 NeurIPS 2025（或 2024）
  ```bash
  make update CONF=neurips YEAR=2025
  ```

- [ ] 步骤 5：确认 manifest 列出 3 个 shard
  ```bash
  cat data/manifest.json | python -m json.tool
  ```
  期望：`shards` 数组长度 3。

---

### 任务 8.2：跑全量测试 + 提交 + 部署

- [ ] 步骤 1：跑测试
  ```bash
  make test
  ```
  期望：全部通过。

- [ ] 步骤 2：本地预览
  ```bash
  make serve
  # 浏览器访问 http://localhost:8000
  # 走一遍任务 6.7 的手动验证清单
  ```

- [ ] 步骤 3：提交并推送
  ```bash
  git add data/raw/ data/shards/ data/manifest.json scrapers/fetch_icml.py
  git commit -m "Add ICML/NeurIPS 2025 raw + shard data"
  git push
  ```

- [ ] 步骤 4：等 GitHub Action 部署完成
  ```bash
  gh run watch
  ```

- [ ] 步骤 5：访问 Pages URL，确认 3 个 shard 都加载，搜索 "transformer" / "diffusion" 等热词出结果。

---

### 任务 8.3：对照设计文档验收清单

逐条勾选 [`docs/specs/2026-04-26-paper-hub-design.md` § 12](../specs/2026-04-26-paper-hub-design.md)：

- [ ] 能跑命令完整抓取 ICLR / ICML / NeurIPS 2025 的 3 个 shard
- [ ] 抓取脚本输出经 schema 校验全部通过
- [ ] `data/manifest.json` 能被前端正确解析
- [ ] 打开网页 3 秒内可搜索（哪怕只有部分 shard 加载完）
- [ ] 输入关键词能在标题+摘要+作者+keywords 中命中
- [ ] 筛选会议、年份能正确过滤
- [ ] 结果项正确显示 presentation 标记（oral 显示，null 不显示）
- [ ] 点击结果跳转到原文页
- [ ] GitHub Pages 部署成功，外网可访问
- [ ] 后续运行 `make update CONF=iclr YEAR=2024` 能新增一片而不影响已有 shard

---

### 任务 8.4：写项目总结

**涉及文件：**
- 新建：`/Users/yupuwang/Documents/code/paper-hub/docs/summary/SUMMARY.md`

- [ ] 步骤 1：参考 CLAUDE.md "项目总结文档规范" 写完整总结，包含当前状态、下一步行动、关键决策与原因、已知坑

- [ ] 步骤 2：commit
  ```bash
  git add docs/summary/SUMMARY.md
  git commit -m "Add MVP summary"
  git push
  ```

---

## 风险与应变

- **OpenReview API 字段位置可能与本计划不一致**：任务 2.3 步骤 2 是手动验证，不符就调字段路径
- **PMLR HTML 结构与 fixture 假设的选择器不一致**：任务 3.3 跑测试时调整选择器
- **ICML 2025 / NeurIPS 2025 还未出榜**：任务 8.1 给出降级方案（先用前一年验证）
- **GitHub Pages 路径问题**：任务 7.2 已经处理过一次；部署后如果 fetch 404，检查 `_site` 目录结构
