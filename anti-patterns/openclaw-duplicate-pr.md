---
type: Anti-Pattern
key: openclaw-duplicate-pr
description: "OpenClaw PR 与已有实现重复"
symptom: "标签包含 duplicate 或 sweeper:implemented-on-main"
trigger_keywords:
  - "duplicate"
  - "implemented-on-main"
fix_action: "1) 搜索已有 PR 和 Issue; 2) 检查 main 分支最新代码; 3) 确认问题是否已解决"
source_pr: "NousResearch/hermes-agent#64639, NousResearch/hermes-agent#53124"
severity: medium
evidence:
  - "NousResearch #64639: 标记 duplicate"
  - "NousResearch #53124: 标记 sweeper:implemented-on-main"
learned_at: 2026-07-15
---

## 反模式说明

贡献者提交的修复 PR 与已有实现重复，或者问题已在 main 分支上解决。

### 触发条件
- 未搜索已有 PR
- 未检查 main 分支最新代码
- Issue 已被其他人修复

### 如何避免
1. 提 PR 前搜索已有 PR 和 Issue
2. 基于最新 main 分支创建分支
3. 在 Issue 中确认是否有人在做
