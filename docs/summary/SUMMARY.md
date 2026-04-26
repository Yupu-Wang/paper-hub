# Paper Hub — 项目总结

**最后更新：** 2026-04-26
**当前 Live URL：** https://yupu-wang.github.io/paper-hub/

---

## 当前状态

### 已完成（MVP 全部交付）

- **数据管道：** 三个独立的 Python fetcher（`fetch_iclr.py` / `fetch_icml.py` / `fetch_neurips.py`），全部基于 OpenReview API v2，输出到 `data/raw/<conf>-<year>.json`
- **构建管道：** `build_shard.py` 校验 schema + 生成带 content-hash 后缀的 shard；`build_manifest.py` 扫描 shards 重写 manifest
- **统一 Schema：** `scrapers/common/schema.py` 用 pydantic 校验，9 个字段（含 `presentation: oral/spotlight/poster/null`）
- **前端：** 原生 HTML/CSS/JS + MiniSearch，无构建链。并行加载 shard，浏览器内构建索引，毫秒级搜索
- **部署：** GitHub Actions → GitHub Pages，工作流监听 `web/**` 与 `data/**` 路径
- **测试：** 42 个 pytest（schema 17 + openreview 16 + build_shard 4 + build_manifest 1 + 其他）
- **数据：** ICLR 2025（3,703）+ ICML 2025（3,257）+ NeurIPS 2025（5,286）= 12,246 篇全部入库并上线

### 未做（明确不在 MVP 范围）

- 历史年份 2021-2024 的回填
- ICML 2021-2022、NeurIPS 2021-2022 的非 OpenReview 数据源（PMLR / papers.nips.cc）的 scraper
- AI 生成中文摘要翻译
- AI 论文一句话总结
- 收藏夹 / 阅读状态
- 安全类、CV 类等其他顶会
- 移动端优化

---

## 下一步行动

如果继续开发，按优先级：

1. **回填历史年份（最容易）：** 直接运行
   ```bash
   make update CONF=iclr YEAR=2024
   make update CONF=iclr YEAR=2023
   make update CONF=icml YEAR=2024
   make update CONF=icml YEAR=2023
   make update CONF=neurips YEAR=2024
   make update CONF=neurips YEAR=2023
   git add data/ && git commit -m "Backfill 2023-2024" && git push
   ```
   ICLR 2021-2022 也在 OpenReview，可以尝试 `make update CONF=iclr YEAR=2021`。

2. **支持 ICML/NeurIPS 老年份：** 需要新增 scraper（PMLR HTML for ICML 2021-2022；papers.nips.cc for NeurIPS 2021-2022）。fetch_icml.py / fetch_neurips.py 中已经有早返回的 SystemExit 占位，按那里的注释扩展。

3. **AI 中文摘要翻译：** 加一个 `scrapers/translate.py`，遍历 raw json 调用翻译 API，把 `abstract_zh` 字段写回。前端搜索时把中文也加入索引。

4. **收藏夹：** 纯前端，用 localStorage 存收藏的 paper.id 列表，加一个 "我的收藏" tab。

---

## 关键决策与原因

| 决策 | 原因 | 排除掉的方案 |
|------|------|-------------|
| **不存 PDF，只链接** | 节省存储；OpenReview 永久公开 | 自己存 PDF 到 HF Datasets / Git LFS |
| **JSON 文件，不要数据库** | 6 万篇内 SQLite/Postgres 都过度设计 | sql.js（WASM 启动慢）、Firebase（违背零成本）|
| **分片：每 conf+year 一个文件** | 增量更新友好 — 浏览器只重下载新增片，旧 shard 缓存命中 | 单一大 JSON（~75MB 一次性下载）|
| **客户端搜索** | 无后端、无配额、无运维 | Algolia（10K 上限）、Meilisearch on HF Space（增加部署）|
| **content-hash 文件名** | 永久强缓存，更新时旧文件名失效 | 文件名固定 + ETag（仍要往返一次）|
| **ICML/NeurIPS 走 OpenReview 而非 PMLR/papers.nips.cc** | 2025 数据全在 OpenReview，已有 abstract+keywords，无需爬 3000 个详情页 | PMLR HTML scraping（慢且脆弱） |
| **抓取脚本不抽象成通用 fetcher** | 三个文件 95% 重复但 YAGNI；以后真要加非 OpenReview 源时再抽象 | 一个 `fetch.py --conf` 通用入口 |
| **MiniSearch 索引在浏览器构建（不预建）** | 浏览器构建 ~500ms 可接受；预建需要 Node.js，引入构建依赖 | Python 端预建 |
| **MVP 只做 2025 单年** | 验证流程；2021-2024 回填只是多跑几次脚本 | 一次性抓 5 年 |

---

## 已知问题与坑

### 已解决

- **OpenReview API v2 字段格式不同：** 官方文档示例用 `decision`（如 `"Accept (oral)"`），但实际 v2 把这信息编码在 `venue` 字段（如 `"ICLR 2025 Oral"`）。`parse_presentation` 已扩展为同时支持两种格式。
- **GitHub Pages 私有仓库不能用：** 免费账号的私有仓库 Pages 是付费功能。改公开后正常。
- **`actions/configure-pages` 的 `enablement: true` 权限不足：** 需要 token 权限来创建 Pages 站点，普通仓库的默认 GITHUB_TOKEN 没有。还是得手动在 Settings 启用 Pages 一次。
- **workflow Prepare site 步骤的 `rm -f _site/data` 失败：** 当时 `_site/data` 是用 `mkdir` 建的目录，`rm -f` 不能删目录。直接去掉这行即可（`web/data` 软链接已经 gitignore 不会被拷过去）。
- **`web/data` 软链接被 git 误追踪：** 第一次 commit 时进了仓库，会破坏 GH Pages 部署。已加入 .gitignore 并 `git rm --cached`。

### 未解决 / 风险

- **OpenReview API 改版风险：** 抓取脚本耦合 v2 API 字段路径。如果 OpenReview 改 schema，所有 fetcher 都要改。raw JSON 已落盘，至少能回溯。
- **首次加载 21MB 略偏重：** 桌面 + 100Mbps 下 5-10 秒可接受，移动网络不友好。如果以后扩到 5 年，需要按需加载（默认只载最新年份）。
- **MiniSearch 中文不友好：** 当前只搜英文。中文翻译加进来后，需要切换 tokenizer 或额外切词。
- **没有 service worker 离线缓存：** 二次加载靠浏览器 HTTP cache（已配置 immutable 强缓存，应该够用）。

---

## 文件位置速查

- 设计文档：[`docs/specs/2026-04-26-paper-hub-design.md`](../specs/2026-04-26-paper-hub-design.md)
- 实施计划：[`docs/plans/2026-04-26-paper-hub-plan.md`](../plans/2026-04-26-paper-hub-plan.md)
- 数据：`data/raw/<conf>-<year>.json` 与 `data/shards/<conf>-<year>.<hash>.json`
- 抓取入口：`scrapers/fetch_<conf>.py`
- 前端入口：`web/index.html` → `web/main.js`
- 部署：`.github/workflows/pages.yml`
