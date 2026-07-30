---
type: Anti-Pattern
key: nousresearch-risk-platform-windows
description: "NousResearch PR 涉及 Windows 平台兼容性"
symptom: "标签包含 sweeper:risk-platform-windows"
trigger_keywords:
  - "risk-platform-windows"
  - "platform-windows"
fix_action: "1) 测试 Windows 平台兼容性; 2) 提供 Windows 特定测试; 3) 考虑跨平台差异"
source_pr: "NousResearch/hermes-agent#52917, NousResearch/hermes-agent#53124"
severity: medium
evidence:
  - "NousResearch #52917: 涉及 Windows 平台，标记 risk-platform-windows"
  - "NousResearch #53124: 涉及 Windows 平台，标记 risk-platform-windows"
learned_at: 2026-07-15
---

## 反模式说明

涉及 Windows 平台兼容性的 PR 风险较高，因为 Windows 和 Unix 系统有差异。

### 触发条件
- 修改文件路径处理
- 修改进程管理
- 修改系统调用

### 如何避免
1. 测试 Windows 平台兼容性
2. 提供 Windows 特定测试
3. 考虑跨平台差异
