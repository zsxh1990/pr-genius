---
type: Anti-Pattern
key: openclaw-needs-real-behavior-proof
description: "OpenClaw PR 需要真实行为证明"
symptom: "标签包含 triage: needs-real-behavior-proof"
trigger_keywords:
  - "needs-real-behavior-proof"
  - "needs proof"
fix_action: "1) 提供真实环境测试结果; 2) 提供复现步骤; 3) 提供测试截图或日志"
source_pr: "openclaw/openclaw#62338"
severity: medium
evidence:
  - "openclaw #62338: 标记 needs-real-behavior-proof"
learned_at: 2026-07-15
---

## 反模式说明

PR 需要提供真实环境下的行为证明，而不仅仅是理论分析。

### 触发条件
- PR 缺少真实环境测试
- PR 只有理论分析
- PR 缺少复现步骤

### 如何避免
1. 提供真实环境测试结果
2. 提供复现步骤
3. 提供测试截图或日志
