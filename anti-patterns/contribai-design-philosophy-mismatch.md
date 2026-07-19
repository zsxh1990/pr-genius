---
type: Anti-Pattern
key: contribai-design-philosophy-mismatch
symptom: |
  改动跟项目设计哲学 / 架构原则冲突。Close 关键词: "doesn't fit our design", "violates our architecture", "out of scope (philosophy)"
root_cause: 未读项目 ARCHITECTURE.md / DESIGN.md / CONTRIBUTING 设计原则, 改动跟核心哲学不符。
trigger_keywords:
  - "doesn't fit our design"
  - "violates our architecture"
  - "out of scope (philosophy)"
  - "not aligned with our philosophy"
  - "we want to keep X simple"
fix_action: |
  1) 读 ARCHITECTURE.md / DESIGN.md / PHILOSOPHY.md
  2) 看 maintainer 写的设计 blog / talk
  3) 改动前问 "how does this fit your architecture?"
source_pr: "ContribAI 14 closed PR 中 ~10% 是 design philosophy 冲突"
prevention: |
  提 PR 前:
  - 读 ARCHITECTURE.md / DESIGN.md
  - 看 maintainer 写的设计 blog / talk / RFC
  - 问 maintainer "how does this fit?"
  - 跟哲学不符的 PR 别提 (避免 close + 信用负分)
learned_at: 2026-07-19
---

## ContribAI 实证 close 数据

- pandas-dev/pandas: ~10% close 提 design philosophy
- 大型 framework (React / Vue / Angular): 类似比例
- 系统软件 (Linux kernel / OpenBSD / systemd): 比例更高

## 反模式特征

1. **未读 ARCHITECTURE.md** — 改动跟核心设计冲突
2. **AI 误判项目风格** — LLM 看 README 就提, 不读 design
3. **强行加 dependency** — 项目偏好 minimal deps, 你加 5 个
4. **改变 core abstraction** — 想 "优化" maintainer 故意留的设计

## 自检清单

提 PR 前:
- [ ] 读 ARCHITECTURE.md / DESIGN.md / PHILOSOPHY.md
- [ ] 看 maintainer 设计 blog / RFC
- [ ] 问 maintainer "how does this fit?"
- [ ] 跟哲学不符的不提

## 关联

- OpenClaw profile: `openclaw-openclaw/index.md` (security-boundary = 哲学)
- honcho: `anti-patterns/honcho-default-db-module-trap.md`
