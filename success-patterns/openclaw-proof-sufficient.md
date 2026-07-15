---
type: Success Pattern
key: openclaw-proof-sufficient
description: "OpenClaw PR 提供充分的 proof of work"
success_factors:
  - "提供测试截图或日志"
  - "提供 PoC 代码"
  - "描述测试环境和复现步骤"
  - "标签包含 proof: sufficient"
repo_requirements:
  - "proof: sufficient 标签"
  - "status: ready for maintainer look"
source_pr: "openclaw/openclaw#106395, openclaw/openclaw#106826"
metrics:
  merge_rate: 0.85
learned_at: 2026-07-15
---

## 成功案例

### PR #106395: fix(device-pair): bound notifier polling overlap

**成功因素**：
1. 提供了详细的测试证据
2. 标签包含 `proof: sufficient`
3. 标签包含 `status: ready for maintainer look`

### PR #106826: fix(gateway): recover when suppressed channel secrets are unavailable

**成功因素**：
1. 提供了详细的测试证据
2. 标签包含 `proof: sufficient`
3. 标签包含 `P0` 优先级
