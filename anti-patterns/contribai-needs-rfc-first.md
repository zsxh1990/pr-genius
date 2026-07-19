---
type: Anti-Pattern
key: contribai-needs-rfc-first
symptom: |
  改动涉及 API 设计 / 架构 / type system 语义, 但没 RFC / design doc / 提前讨论。Close 关键词: "needs RFC", "open an issue first", "please discuss design", "this is too big for a PR"
root_cause: 涉及设计的改动直接提 PR, 没 RFC 流程。
trigger_keywords:
  - "needs RFC"
  - "open an issue first"
  - "please discuss design"
  - "this is too big for a PR"
  - "RFC process required"
  - "design discussion needed"
fix_action: |
  1) 大改动 (API / 架构 / type system) 必须先 RFC
  2) 在 issue 区开 "RFC: <title>" 讨论
  3) maintainer 同意后再提 PR
  4) PR body 引用 RFC issue 链接
source_pr: "astral-sh/ty type system 改动, HolmesGPT operator mode"
prevention: |
  涉及设计的改动:
  - 先在 issue 开 RFC (项目可能有 .github/RFC_TEMPLATE.md)
  - maintainer 同意后再提 PR
  - PR body 必含 RFC 链接
  - 不直接提大改 PR (信用负分 + close)
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- astral-sh/ty (type system 改动): ~25% close 是 "needs design discussion"
- HolmesGPT/holmesgpt (operator mode): ~20% close 是 "needs RFC"
- pandas-dev/pandas (3.0 roadmap): 类似比例
- 大型 framework: 15-25% close 是 RFC 流程未走

## 反模式特征

1. **跳过 RFC** — 大改直接提 PR
2. **未在 issue 讨论** — maintainer 没参与设计
3. **设计已定, 想改** — 改 maintainer 故意留的设计
4. **跨模块改动** — 影响多个 sub-system, 需要 maintainer 协调
5. **新增 public API** — 不可逆, 需要 RFC

## 自检清单

提 PR 前:
- [ ] 改动涉及 API / 架构 / type system?
- [ ] 项目有 RFC 流程?
- [ ] 在 issue 开 RFC + 等待 maintainer 同意
- [ ] PR body 引用 RFC issue

## 关联

- astral-sh-ty profile: type system 改动需 RFC
- HolmesGPT profile: operator mode 改动需 RFC
