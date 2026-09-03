---
type: Anti-Pattern
key: transformers-ci-security-gate
repo: huggingface/transformers
description: "CI 安全门禁阻止合并"
symptom: "CI Security Gate 自动批准被阻止"
trigger_keywords:
  - "ci security gate"
  - "automatic approval blocked"
fix_action: "检查代码是否引入安全风险，确保 CI 完整通过"
severity: high
source_pr: "huggingface/transformers#48038"
evidence:
  - "huggingface 有 CI 安全门禁，自动检查代码安全性"
  - "外部贡献者的 PR 需要额外的安全审查"
learned_at: 2026-08-17
---

## 反模式说明

CI 安全门禁阻止合并

### 触发条件

CI Security Gate 自动批准被阻止

### 为什么这是反模式

1. huggingface 有 CI 安全门禁，自动检查代码安全性
2. 外部贡献者的 PR 需要额外的安全审查

### 如何避免

检查代码是否引入安全风险，确保 CI 完整通过
