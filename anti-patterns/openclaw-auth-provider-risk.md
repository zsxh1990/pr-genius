---
type: Anti-Pattern
key: openclaw-auth-provider-risk
description: "OpenClaw PR 涉及认证提供者，风险较高"
symptom: "标签包含 merge-risk: auth-provider"
trigger_keywords:
  - "auth-provider"
  - "merge-risk: auth-provider"
fix_action: "1) 测试认证流程; 2) 测试边界情况; 3) 提供回滚方案"
source_pr: "openclaw/openclaw#103118, NousResearch/hermes-agent#52865"
severity: high
evidence:
  - "openclaw #103118: 涉及 auth-provider，标记 risk-auth-provider"
  - "NousResearch #52865: 涉及 Google AI Studio 认证"
learned_at: 2026-07-15
---

## 反模式说明

涉及认证提供者的 PR 风险较高，可能导致认证失败或安全问题。

### 触发条件
- 修改认证逻辑
- 修改凭证存储
- 修改权限检查

### 如何避免
1. 测试认证流程
2. 测试边界情况（过期、刷新、撤销）
3. 提供回滚方案
