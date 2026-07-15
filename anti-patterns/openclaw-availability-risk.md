---
type: Anti-Pattern
key: openclaw-availability-risk
description: "OpenClaw PR 涉及可用性，风险较高"
symptom: "标签包含 merge-risk: availability"
trigger_keywords:
  - "availability"
  - "merge-risk: availability"
fix_action: "1) 测试服务可用性; 2) 提供降级方案; 3) 测试高并发场景"
source_pr: "openclaw/openclaw#90421"
severity: high
evidence:
  - "openclaw #90421: 涉及可用性，标记 risk-availability"
learned_at: 2026-07-15
---

## 反模式说明

涉及服务可用性的 PR 风险较高，可能导致服务不可用。

### 触发条件
- 修改服务启动逻辑
- 修改服务健康检查
- 修改服务降级逻辑

### 如何避免
1. 测试服务可用性
2. 提供降级方案
3. 测试高并发场景
