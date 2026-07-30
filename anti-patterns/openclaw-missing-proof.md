---
type: Anti-Pattern
key: openclaw-missing-proof
description: "OpenClaw PR 缺少 proof of work"
symptom: "标签包含 needs proof 或 status: needs proof"
trigger_keywords:
  - "needs proof"
  - "needs proof"
fix_action: "1) 提供测试截图或日志; 2) 提供 PoC 代码; 3) 描述测试环境"
source_pr: "openclaw/openclaw#104817"
severity: medium
evidence:
  - "openclaw #104817: 标记 needs proof"
learned_at: 2026-07-15
---

## 反模式说明

OpenClaw 要求外部 PR 提供 proof of work（测试截图、日志、PoC 代码等）。

### 触发条件
- PR 没有提供测试证据
- PR 描述不够详细
- 缺少复现步骤

### 如何避免
1. 提供测试截图或日志
2. 提供 PoC 代码
3. 描述测试环境和复现步骤
