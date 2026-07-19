---
type: Anti-Pattern
key: contribai-first-time-large-repo
symptom: |
  首次贡献者向 ≥10k star 仓提 PR, 信用未建立。Close 关键词: "first contribution, please discuss in issue first", "out of scope for new contributor", "this is too complex"
root_cause: 首次贡献者向大仓提 PR 没建立信用, 维护者默认怀疑 (信用模型).
trigger_keywords:
  - "first contribution"
  - "first time"
  - "please discuss in issue first"
  - "out of scope (new contributor)"
  - "this is too complex for a new contributor"
fix_action: |
  1) 先在 issue 区建立信任 (回复 5+ 个其他 issue)
  2) 提简单 fix (typo / docs 补 example) 建立信用
  3) 再提复杂 PR
source_pr: "pallets/flask + pandas-dev/pandas 首次贡献者合并率 < 5%"
prevention: |
  首次贡献大仓:
  - 先 issue 区参与 2-4 周 (评论 / 提想法)
  - 先提 typo / docs 补 example 简单 PR
  - 再提功能 / bug fix 复杂 PR
  - 信用需要时间积累
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pallets/flask: 首次贡献者合并率 < 5%
- pandas-dev/pandas: 首次贡献者合并率 < 3%
- NousResearch/hermes-agent: 首次贡献者合并率 ~20% (友好社区)
- OpenClaw: 首次贡献者合并率 ~10% (ClawSweeper 评分严)

## 反模式特征

1. **首次就提大改** — 没信用就改 core
2. **未参与 issue 区** — 没建立 maintainer 信任
3. **AI agent 一次性批量提** — 信用模型崩
4. **PR 撞新功能而非 bug fix** — 新贡献者提 feature 失败率高

## 自检清单

提 PR 前:
- [ ] 在 issue 区参与 2-4 周
- [ ] 提简单 PR 先建立信用
- [ ] 这次是 typo / docs / 简单 bug fix 吗?
- [ ] PR 不会撞 maintainer 路线?

## 关联

- evaluator signal: first_contributor_large_repo (severity=medium)
- pallets/pandas profile: 信用模型
