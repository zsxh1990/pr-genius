---
type: Anti-Pattern
key: vercel-failing-tests
repo: vercel/next.js
description: "PR 导致测试失败或性能回归"
symptom: "CI 报告显示测试失败或指标回归"
trigger_keywords:
  - "failing test"
  - "regression"
  - "🔴"
fix_action: "本地运行测试确保通过，检查性能指标无回归"
severity: high
source_pr: "vercel/next.js#97448, vercel/next.js#96954"
evidence:
  - "next.js 有严格的 CI 门禁，测试失败直接阻止合并"
  - "性能回归会被自动检测并阻止"
learned_at: 2026-08-17
---

## 反模式说明

PR 导致测试失败或性能回归

### 触发条件

CI 报告显示测试失败或指标回归

### 为什么这是反模式

1. next.js 有严格的 CI 门禁，测试失败直接阻止合并
2. 性能回归会被自动检测并阻止

### 如何避免

本地运行测试确保通过，检查性能指标无回归
