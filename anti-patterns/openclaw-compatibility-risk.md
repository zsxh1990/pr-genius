---
type: Anti-Pattern
key: openclaw-compatibility-risk
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 存在兼容性风险"
symptom: "标签包含 merge-risk: compatibility"
trigger_keywords:
  - "compatibility"
  - "merge-risk: compatibility"
fix_action: "1) 测试向后兼容性; 2) 提供迁移指南; 3) 使用 feature flag"
source_pr: "openclaw/openclaw#104514, openclaw/openclaw#62338"
severity: medium
evidence:
  - "openclaw #104514: 存在兼容性风险"
  - "openclaw #62338: 存在兼容性风险"
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-compatibility-risk.md
updated: 2026-08-01
confidence: medium

---

## 反模式说明

PR 改动可能破坏现有功能的兼容性。

### 触发条件
- 修改 API 接口
- 修改配置格式
- 修改默认行为

### 如何避免
1. 测试向后兼容性
2. 提供迁移指南
3. 使用 feature flag 控制新行为

## Applicability

All repository sizes.
