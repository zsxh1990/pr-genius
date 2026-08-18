---
type: Anti-Pattern
key: transformers-code-agent-slop
repo: huggingface/transformers
description: "PR 被标记为 AI 生成的低质量代码"
symptom: "标签包含 "Code agent slop""
trigger_keywords:
  - "code agent slop"
fix_action: "确保代码经过人工审查，理解每行改动的原因"
severity: high
source_pr: "huggingface/transformers#47837"
evidence:
  - "维护者对 AI 生成的 PR 持怀疑态度"
  - "需要展示对代码的理解和人工干预"
learned_at: 2026-08-17
---

## 反模式说明

PR 被标记为 AI 生成的低质量代码

### 触发条件

标签包含 "Code agent slop"

### 为什么这是反模式

1. 维护者对 AI 生成的 PR 持怀疑态度
2. 需要展示对代码的理解和人工干预

### 如何避免

确保代码经过人工审查，理解每行改动的原因
