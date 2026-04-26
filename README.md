# Paper Hub

顶会论文搜索网站。MVP：ICLR / ICML / NeurIPS 2025。

- 设计：[docs/specs/2026-04-26-paper-hub-design.md](docs/specs/2026-04-26-paper-hub-design.md)
- 实施计划：[docs/plans/2026-04-26-paper-hub-plan.md](docs/plans/2026-04-26-paper-hub-plan.md)

## 快速开始

```bash
conda activate paper-hub
make update CONF=iclr YEAR=2025
make update CONF=icml YEAR=2025
make update CONF=neurips YEAR=2025
make serve  # 本地预览
```
