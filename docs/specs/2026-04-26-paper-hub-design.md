# Paper Hub 设计文档

**日期：** 2026-04-26
**状态：** 待最终确认

---

## 1. 背景与目标

建一个个人用的顶会论文检索网站，用来快速搜到感兴趣的论文并跳转原文阅读。

**核心目标：**
- **MVP 范围：** 仅覆盖 ICLR / ICML / NeurIPS **2025 年**全部录取论文（共 3 个 shard）
- 架构必须支持后续按"会议-年份"维度逐步扩展（最终目标 2021-2025 共 15 个 shard）
- 关键词搜索（标题 + 摘要 + 作者 + 关键词），毫秒级响应
- 按会议、年份、作者筛选
- 桌面浏览器使用，零服务器成本
- 每个"会议-年份"独立可更新

**Non-goals（MVP 明确不做，未来可加）：**
- 不存 PDF（只链接到原文页，原文页本身有 PDF 入口）
- 不做相似论文推荐
- 不做用户系统、笔记、评论
- 不做手机端优化（默认能用即可）
- 不做中文搜索英文论文
- 不做安全类会议（CCS / USENIX 等）

**未来可能扩展（不在 MVP 范围）：**
- AI 自动生成中文摘要翻译
- AI 自动生成论文一句话总结
- 历史年份回填（2021-2024）
- 安全类、CV 类等其他顶会

---

## 2. 架构总览

**部署：** GitHub Pages，纯静态。

**数据流：**

```
[Python 抓取脚本] → data/raw/<conf>-<year>.json
       ↓ build
[Python 构建脚本] → data/shards/<conf>-<year>.json + data/manifest.json
       ↓ git push
[GitHub Pages 静态托管]
       ↓ 浏览器访问
[前端] 拉 manifest → 并行拉 shards → 内存中构建 MiniSearch 索引 → 用户搜索
```

**关键决策：**
- **不要数据库**：JSON 文件足够，6 万篇内无压力
- **分片存储**：每个"会议-年份"一个 shard 文件 → 增量更新友好（更新某一片不影响其他片的浏览器缓存）
- **客户端搜索**：MiniSearch 在浏览器内构建索引、运行查询，无后端

---

## 3. 统一元数据 Schema

所有会议的论文必须输出成相同的 JSON 结构。每篇论文是一个对象：

```json
{
  "id": "iclr-2025-1234",
  "title": "Attention Is All You Need (Again)",
  "authors": ["Alice Smith", "Bob Lee"],
  "abstract": "We propose ...",
  "keywords": ["attention", "transformer"],
  "conference": "ICLR",
  "year": 2025,
  "url": "https://openreview.net/forum?id=abc123",
  "presentation": "oral"
}
```

**字段定义：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | `<conf>-<year>-<seq>`，全部小写，全局唯一 |
| `title` | string | ✅ | 论文标题，去除前后空白 |
| `authors` | string[] | ✅ | 作者全名，按官方顺序，机构名不放进来 |
| `abstract` | string | ✅ | 完整摘要，去除前后空白；缺失时填空字符串 |
| `keywords` | string[] | ✅ | 论文自带的关键词；没有就 `[]` |
| `conference` | string | ✅ | 大写枚举：`ICLR` / `ICML` / `NeurIPS` |
| `year` | number | ✅ | 4 位整数，如 `2025` |
| `url` | string | ✅ | 论文详情页（OpenReview / PMLR），用户点击跳转的目标 |
| `presentation` | string \| null | ⚠️ | 枚举：`oral` / `spotlight` / `poster` / `null`（数据源未提供时填 `null`） |

**`presentation` 字段各会议数据源情况：**

| 会议 | 是否能获取 | 说明 |
|------|-----------|------|
| ICLR | ✅ | OpenReview `decision` 字段含 "Accept (oral)" / "Accept (spotlight)" / "Accept (poster)"，按字符串解析 |
| NeurIPS（OpenReview 年份） | ✅ | 同 ICLR |
| ICML | ❌ | PMLR 不区分，统一填 `null` |
| NeurIPS（papers.nips.cc 年份） | ⚠️ | 详情页可能有，写脚本时确认；拿不到就填 `null` |

**Schema 校验：** `scrapers/common/schema.py` 提供 `validate(paper: dict) -> None`，所有抓取脚本输出后必须过校验。校验失败的条目不写入，并打日志。

---

## 4. 各会议数据获取方案

每个"会议-年份"独立成一个抓取任务，对应一条命令。脚本结构：

```
scrapers/
  fetch_iclr.py       # python -m scrapers.fetch_iclr --year 2025
  fetch_icml.py       # python -m scrapers.fetch_icml --year 2025
  fetch_neurips.py    # python -m scrapers.fetch_neurips --year 2025
  build_shard.py      # 把 raw/<conf>-<year>.json 转成 shards/<conf>-<year>.json
  build_manifest.py   # 扫描 shards/ 目录，重写 manifest.json
  common/
    schema.py
    openreview_client.py
```

**MVP 只抓 2025 年；以下方案描述支持 2021-2025 全年份的设计，便于将来扩展。**

### 4.1 ICLR

- **数据源：** OpenReview，全年份统一
- **库：** `openreview-py`（v2 API）
- **Venue ID：** `ICLR.cc/{year}/Conference`
- **筛选条件：** `decision` 字段以 `Accept` 开头（包括 oral / spotlight / poster）
- **`presentation` 推断：** 从 `decision` 字符串提取（`accept (oral)` → `oral` 等）

### 4.2 ICML

- **数据源：** PMLR proceedings（`proceedings.mlr.press/v{volume}/`）
- **库：** `requests` + `beautifulsoup4`
- **卷号映射（写到代码里的常量表）：**
  - 2021 → v139
  - 2022 → v162
  - 2023 → v202
  - 2024 → v235
  - 2025 → 抓取时去 PMLR 站点查最新卷号
- **抓取流程：** 拉 volume 索引页 → 遍历每篇论文的详情页 → 提取 title / authors / abstract
- **keywords：** PMLR 不提供，统一填 `[]`
- **presentation：** PMLR 不区分，统一填 `null`

### 4.3 NeurIPS

NeurIPS 数据源按年份分裂，**一个脚本内部分支**：

- **2021-2022：** `papers.nips.cc`（有结构化页面）
  - 索引页：`https://papers.nips.cc/paper_files/paper/{year}`
  - 详情页有 abstract
  - presentation：详情页可能有 oral/spotlight 标记，抓取时尝试解析；拿不到就 `null`
- **2023-2025：** OpenReview（`NeurIPS.cc/{year}/Conference`）
  - 复用 `common/openreview_client.py`，逻辑同 ICLR

**统一处理：** `fetch_neurips.py --year` 内部根据年份选择数据源，输出格式一致。

### 4.4 共同约定

- 每个抓取脚本输出到 `data/raw/<conf>-<year>.json`，结构：

  ```json
  {
    "conference": "ICLR",
    "year": 2025,
    "fetched_at": "2026-04-26T15:30:00+08:00",
    "source": "openreview",
    "papers": [ {...}, {...} ]
  }
  ```

- 抓取脚本必须支持**断点续抓**：遇到网络错误退避重试 3 次，每条论文独立失败不影响整体
- 抓取过程显示进度条（`tqdm`）

---

## 5. 构建步骤

### 5.1 `build_shard.py`

```bash
python -m scrapers.build_shard --conf iclr --year 2025
```

读 `data/raw/iclr-2025.json` → 校验 schema → 输出 `data/shards/iclr-2025.json`：

```json
{
  "conference": "ICLR",
  "year": 2025,
  "count": 2300,
  "built_at": "2026-04-26T15:35:00+08:00",
  "papers": [ {...}, {...} ]
}
```

**注意：** 索引在前端构建（MiniSearch 在浏览器跑，5MB shard 约 500ms 索引时间），shard 不含预构建索引。理由：
- Python 端预建 MiniSearch 索引需要 Node.js，引入额外依赖
- 浏览器端构建可接受
- 减少 shard 体积

### 5.2 `build_manifest.py`

```bash
python -m scrapers.build_manifest
```

扫描 `data/shards/` 所有文件，生成 `data/manifest.json`：

```json
{
  "built_at": "2026-04-26T15:35:00+08:00",
  "shards": [
    { "conference": "ICLR", "year": 2025, "count": 2300, "file": "shards/iclr-2025.a1b2c3.json", "size_bytes": 5400000 },
    { "conference": "ICML", "year": 2025, "count": 2600, "file": "shards/icml-2025.d4e5f6.json", "size_bytes": 5800000 },
    { "conference": "NeurIPS", "year": 2025, "count": 4000, "file": "shards/neurips-2025.789abc.json", "size_bytes": 9200000 }
  ]
}
```

---

## 6. 前端设计

### 6.1 页面布局

单页应用，三栏：

```
┌─────────────────────────────────────────────────────┐
│  Paper Hub                          加载进度: 3/3   │
├──────────────┬──────────────────────────────────────┤
│ [搜索框]      │  [搜索结果列表]                        │
│              │                                      │
│ 会议         │  - ICLR 2025 · oral                  │
│ ☑ ICLR       │    Attention Is All You Need...      │
│ ☑ ICML       │    Alice Smith, Bob Lee              │
│ ☑ NeurIPS    │    [摘要前 200 字预览]                  │
│              │                                      │
│ 年份         │  - ICML 2025                         │
│ ☑ 2025       │    ...                               │
│              │                                      │
│ 作者搜索      │                                      │
│ [____]       │                                      │
└──────────────┴──────────────────────────────────────┘

> MVP 阶段年份筛选只有 2025，UI 仍按多选实现，未来加更多年时无需改代码。
```

### 6.2 交互细节

- **搜索：** 输入即时触发（debounce 200ms），搜索字段：`title` + `abstract` + `authors` + `keywords`
- **多关键词：** 默认 AND；引号包起来视为短语；`OR` 大写视为或运算（MiniSearch 原生支持）
- **筛选：** 多选，组合是 AND
- **结果排序：** 默认按搜索相关度（MiniSearch score）；提供下拉切换"按年份新→旧"
- **结果项：** 显示标题、会议+年份+presentation（如 `ICLR 2025 · oral`，`presentation` 为 null 时省略不显示）、作者、摘要预览（前 200 字截断），整项可点击跳到 `url`
- **分页：** 每页 50 条，无限滚动（Intersection Observer）
- **空查询：** 不显示结果（避免渲染所有论文卡死浏览器）；显示一句"输入关键词或选择筛选条件"

### 6.3 加载策略

1. 页面打开 → 拉 `data/manifest.json`
2. 立即渲染 UI 框架（搜索框、筛选侧边栏占位）
3. 并行拉所有 shard（浏览器 6 并发自动调度）
4. 每个 shard 拉到后立即合并到内存数据集 + 加入 MiniSearch 索引；顶部进度条形如 `2/3`
5. 全部加载后，进度条隐藏

**HTTP 缓存：** shard 文件用强缓存（`Cache-Control: max-age=31536000, immutable`），文件名带内容 hash 后缀做缓存破坏（如 `iclr-2025.a1b2c3.json`，由 build 步骤生成，manifest 里指向最新版本）。

### 6.4 技术栈

- **HTML/CSS/JS：** 原生，无框架
- **搜索库：** [MiniSearch](https://github.com/lucaong/minisearch) (~10KB gzipped)
- **打包：** 不打包（直接 `<script type="module">`）
- **样式：** 手写 CSS，~200 行内
- **部署：** GitHub Actions 把 `web/` + `data/` 推到 `gh-pages` 分支，GitHub Pages 自动发布

---

## 7. 更新工作流

**MVP 阶段一次性建库（跑 3 遍即可）：**

```bash
make update CONF=iclr    YEAR=2025
make update CONF=icml    YEAR=2025
make update CONF=neurips YEAR=2025
git add data/ && git commit -m "Initial 2025 corpus" && git push
```

**未来新会议出来后（例如要补 ICLR 2024 或新增 NeurIPS 2026），单条命令：**

```bash
make update CONF=iclr YEAR=2024
git add data/ && git commit -m "Add ICLR 2024" && git push
# GitHub Action 自动部署，几分钟后网站更新
# 旧 shard 文件不变 → 用户浏览器缓存命中，只下载新增的那一片
```

**Makefile 实现：**

```makefile
update:
	python -m scrapers.fetch_$(CONF) --year $(YEAR)
	python -m scrapers.build_shard --conf $(CONF) --year $(YEAR)
	python -m scrapers.build_manifest
```

---

## 8. 项目结构

```
paper-hub/
├── README.md
├── Makefile
├── docs/
│   ├── specs/
│   │   └── 2026-04-26-paper-hub-design.md      ← 本文件
│   ├── plans/
│   └── summary/
├── scrapers/
│   ├── __init__.py
│   ├── fetch_iclr.py
│   ├── fetch_icml.py
│   ├── fetch_neurips.py
│   ├── build_shard.py
│   ├── build_manifest.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── openreview_client.py
│   └── requirements.txt
├── data/
│   ├── raw/                     # 抓取原始输出，git 提交（便于回溯）
│   │   ├── iclr-2025.json       # MVP 阶段只有 3 个文件
│   │   ├── icml-2025.json
│   │   └── neurips-2025.json
│   ├── shards/                  # 前端消费的 shard（带 hash 后缀）
│   │   ├── iclr-2025.a1b2c3.json
│   │   ├── icml-2025.d4e5f6.json
│   │   └── neurips-2025.789abc.json
│   └── manifest.json
├── web/
│   ├── index.html
│   ├── main.js
│   ├── search.js
│   ├── styles.css
│   └── lib/
│       └── minisearch.min.js
├── tests/
│   ├── test_schema.py
│   └── test_build_shard.py
└── .github/
    └── workflows/
        └── pages.yml            # build & deploy
```

---

## 9. 技术栈与环境

- **Python：** 3.11+，使用 conda 环境（项目专属，名字 `paper-hub`）
- **核心依赖：**
  - `openreview-py` （ICLR / NeurIPS 2023+）
  - `requests` + `beautifulsoup4`（PMLR、papers.nips.cc）
  - `tqdm`（进度条）
  - `pydantic` 或手写校验（schema 校验）
- **前端：** 无构建链，原生 ES module
- **部署：** GitHub Pages + GitHub Actions

---

## 10. 数据规模与性能预估

| 项目 | MVP（2025 单年） | 满配（2021-2025） |
|------|----------------|------------------|
| 单篇 metadata（含摘要） | ~2 KB | ~2 KB |
| 单 shard（约 2500 篇） | ~5 MB raw / ~1.5 MB gzipped | 同 |
| Shard 总数 | **3 个**（3 会议 × 1 年） | 15 个（3 会议 × 5 年） |
| 全量下载 | **~15 MB raw / ~5 MB gzipped** | ~75 MB raw / ~22 MB gzipped |
| 浏览器内存占用（含索引） | ~30-50 MB | ~150-200 MB |
| 首次加载耗时（100 Mbps） | **<2 秒** | ~3-5 秒 |
| 二次加载（命中缓存） | <500ms | <500ms |
| 单次搜索响应 | <50ms | <50ms |

MVP 体感非常轻；满配也在桌面浏览器舒适区。

---

## 11. 风险与未决事项

| 风险 | 应对 |
|------|------|
| OpenReview API 改版 | 抓取脚本独立、易改；raw JSON 已落盘可回溯 |
| PMLR HTML 结构变化 | 同上；增加 schema 校验报错 |
| NeurIPS 2025 是否在 OpenReview | 写脚本时再确认；若不在则补充新分支 |
| GitHub Pages 单仓库 1 GB 限制 | 当前 75MB，5 年内无忧；超出可迁 Cloudflare Pages |
| 前端首次加载 22MB 体感偏慢 | 进度条 + service worker 缓存；如真的慢再加按需加载 |
| 论文摘要里有 LaTeX 公式 | 搜索时按字面处理；显示时不渲染（保留原文） |

---

## 12. 验收标准（MVP 完成的标志）

- [ ] 能跑命令完整抓取 ICLR / ICML / NeurIPS **2025** 的 3 个 shard
- [ ] 抓取脚本输出经 schema 校验全部通过
- [ ] `data/manifest.json` 能被前端正确解析
- [ ] 打开网页 3 秒内可搜索（哪怕只有部分 shard 加载完）
- [ ] 输入关键词能在标题+摘要+作者+keywords 中命中
- [ ] 筛选会议、年份能正确过滤
- [ ] 结果项正确显示 presentation 标记（oral 显示，null 不显示）
- [ ] 点击结果跳转到原文页
- [ ] GitHub Pages 部署成功，外网可访问
- [ ] 后续运行 `make update CONF=iclr YEAR=2024` 能新增一片而不影响已有 shard
