---
type: Anti-Pattern
key: module-refactored-approach-obsolete
description: "PR 方案因目标模块被重构而失效"
symptom: "maintainer 评论: this PR's approach no longer applies to current main"
trigger_keywords:
  - "no longer applies"
  - "refactored into"
  - "module was moved"
fix_action: "1) 检查目标模块是否在最近 commit 中被重构; 2) 在 Issue 中确认方案是否仍适用; 3) 基于最新 main 重新实现"
source_pr: "openclaw/openclaw#102368"
severity: medium
evidence:
  - "openclaw #102368: crestodian 模块被重构到 system-agent，PR 方案失效"
learned_at: 2026-07-15
---

## 反模式说明

PR 方案基于的代码模块在提交后被重构或移动，导致方案不再适用。

### 触发条件
- PR 打开时间过长（>1 周）
- 目标模块被 maintainer 重构
- PR 基于旧代码结构

### 为什么这是反模式
1. 维护者无法合并已过时的代码
2. Review 成本浪费
3. 贡献者时间浪费

### 如何避免
1. PR 打开后尽快完成，避免长时间挂起
2. 定期 rebase on latest main
3. 提 PR 前检查目标模块最近是否有重构
