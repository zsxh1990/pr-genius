---
type: Anti-Pattern
key: contribai-docs-pr-missing-quickstart
symptom: |
  docs-only PR 但缺 quickstart / install / 关键示例, 撞维护者已有规划。Close 关键词: "docs already planned", "contribute to docs PR #N", "in our roadmap"
root_cause: docs-only PR 撞维护者已有 docs 重写计划, 维护者已经在做类似改动。
trigger_keywords:
  - "docs already planned"
  - "contribute to docs PR #N"
  - "in our roadmap"
  - "docs are being rewritten"
  - "see docs issue #N"
fix_action: |
  1) 搜 issue 区 "docs" / "documentation" 关键词
  2) 看 maintainer 是否已经在写 docs
  3) 提 PR 前问 "should I contribute to existing docs effort?"
source_pr: "pallets/flask ~15% close 是 docs-only 撞规划"
prevention: |
  docs-only PR 慎提:
  - 先搜 issue 区 docs 关键词
  - 看 maintainer 是否有 docs 重写计划
  - 问 "should I contribute to existing effort?"
  - docs PR 优先作为 supplement (补 missing example), 不重写
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pallets/flask: ~15% close 是 docs-only 撞规划
- pandas-dev/pandas: docs PR 占 close ~10%
- 大型 framework 通用: docs PR 失败率 30-50%

## 反模式特征

1. **docs-only 改动** — 没代码, 只改 README / docs
2. **撞维护者已有规划** — maintainer 已经在重写 docs
3. **覆盖不必要** — 维护者觉得 "已经够好了"
4. **改错位置** — example 在 repo 里 vs 在 docs site

## 自检清单

提 docs PR 前:
- [ ] 搜 issue "docs" / "documentation" 关键词
- [ ] 看 maintainer 是否有 docs 重写计划
- [ ] 改的是 example 补 missing 还是 coverage 重写
- [ ] 在 issue 问 maintainer "should I contribute?"

## 关联

- pallets-flask/index.md: docs-only 是 top 3 close 原因
