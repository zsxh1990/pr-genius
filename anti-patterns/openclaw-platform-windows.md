---type: Anti-Pattern
key: openclaw-platform-windows
tags: [cron, scheduling, reliability]
description: "OpenClaw PR 涉及 Windows 平台兼容性"
symptom: "标签包含 platform/windows"
trigger_keywords:
  - "platform/windows"
  - "windows"
fix_action: "1) 测试 Windows 平台兼容性; 2) 提供 Windows 特定测试; 3) 考虑跨平台差异"
source_pr: "NousResearch/hermes-agent#52917, NousResearch/hermes-agent#53124"
severity: medium
evidence:
  - "NousResearch #52917: 涉及 Windows 平台"
  - "NousResearch #53124: 涉及 Windows 平台"
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/openclaw-platform-windows.md
updated: 2026-08-01
confidence: medium
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

## Applicability

All repository sizes.
