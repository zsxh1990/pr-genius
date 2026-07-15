---
type: Anti-Pattern
key: openclaw-security-boundary-risk
description: "OpenClaw PR 涉及安全边界改动，审查更严格"
symptom: "标签包含 merge-risk: security-boundary"
trigger_keywords:
  - "security-boundary"
  - "auth-provider"
  - "credentials"
fix_action: "1) 提供详细的安全分析; 2) 包含 PoC 或测试; 3) 遵循最小权限原则"
source_pr: "openclaw/openclaw#103118, NousResearch/hermes-agent#52865"
severity: high
evidence:
  - "openclaw #103118: 涉及 auth-provider，审查更严格"
  - "NousResearch #52865: 涉及 Google AI Studio 认证"
learned_at: 2026-07-15
---

## 反模式说明

涉及安全边界（认证、授权、凭证）的 PR 审查更严格，合并率更低。

### 触发条件
- 修改认证逻辑
- 修改凭证存储
- 修改权限检查

### 如何避免
1. 提供详细的安全分析说明
2. 包含 PoC 或测试证明安全性
3. 遵循最小权限原则
4. 避免修改核心认证逻辑，除非必要
