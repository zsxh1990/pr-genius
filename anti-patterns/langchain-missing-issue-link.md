---
type: Anti-Pattern
key: langchain-missing-issue-link
repo: langchain-ai/langchain
description: "PR 未关联 Issue，被 require-issue-link bot 自动关闭"
symptom: "PR 被标记 missing-issue-link 后自动关闭"
trigger_keywords:
  - "missing-issue-link"
  - "require-issue-link"
fix_action: "先创建 Issue 讨论方案，再提 PR 并添加 Fixes #NNN"
severity: critical
source_pr: "langchain-ai/langchain#39701, langchain-ai/langchain#39694"
evidence:
  - "langchain 使用 require-issue-link bot 自动关闭无 Issue 关联的 PR"
  - "外部贡献者必须先在 Issue 中获得认可才能提 PR"
learned_at: 2026-08-17
---

## 反模式说明

PR 未关联 Issue，被 require-issue-link bot 自动关闭

### 触发条件

PR 被标记 missing-issue-link 后自动关闭

### 为什么这是反模式

1. langchain 使用 require-issue-link bot 自动关闭无 Issue 关联的 PR
2. 外部贡献者必须先在 Issue 中获得认可才能提 PR

### 如何避免

先创建 Issue 讨论方案，再提 PR 并添加 Fixes #NNN
