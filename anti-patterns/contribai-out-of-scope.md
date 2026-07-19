---
type: Anti-Pattern
key: contribai-out-of-scope
symptom: |
  改动跟维护者路线 / 项目目标不一致。Close 关键词: "out of scope", "not in roadmap", "off-topic"
root_cause: 提交前未看项目 ROADMAP / CONTRIBUTING 路线图, 不知道哪些方向维护者明确不收。
trigger_keywords:
  - "out of scope"
  - "not in roadmap"
  - "off-topic"
  - "would visit this in the future"
  - "we don't take this kind of PR"
fix_action: |
  1) 读 CONTRIBUTING.md / ROADMAP.md / docs/ 找出"明确不收"清单
  2) 看最近 100 个 closed PR 的 close 原因分布
  3) 在 Issue 区先问维护者 "would you accept a PR for <X>?"
source_pr: "pandas-dev/pandas ~40% close 是 Out of scope (ContribAI v2 调研)"
prevention: |
  提 PR 前必做:
  - 读 CONTRIBUTING.md 找 "out of scope" / "not accepted" 章节
  - 看最近 closed PR 找 close 关键词 top 5
  - 跟 3.0 / 2.0 roadmap 对齐 (大项目)
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pandas-dev/pandas: **~40%** close 是 Out of scope (头号杀手)
- pallets/flask: ~25% (vs 改文档撞规划)
- 大仓通用: 10-40% close 是 Out of scope

## 反模式特征

1. **跟维护者路线冲突** — 改动不在 roadmap
2. **想加新功能但项目不收** — "想加 feature X, 但维护者已决定不做"
3. **替代方案分歧** — 维护者选了别的实现路径
4. **AI 误判项目范围** — AI 看 README 就提, 不看 CONTRIBUTING

## 自检清单

提 PR 前:
- [ ] 读 CONTRIBUTING.md / ROADMAP.md
- [ ] 看最近 50-100 closed PR close 关键词
- [ ] 在 Issue 区确认 "would you accept?"
- [ ] 改动跟 3.0 / 2.0 roadmap 对齐 (大项目)

## 关联

- pandas profile: `pandas-dev-pandas/index.md` (Out of scope 占 40%)
- policy: docs/policies/pandas-dev-pandas.md (待 P1 扩)
