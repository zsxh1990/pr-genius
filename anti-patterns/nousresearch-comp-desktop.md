---
type: Anti-Pattern
key: nousresearch-comp-desktop
description: "NousResearch 桌面端 PR 风险较高"
symptom: "标签包含 comp/desktop"
trigger_keywords:
  - "comp/desktop"
  - "desktop"
fix_action: "1) 测试桌面端兼容性; 2) 提供桌面端特定测试; 3) 考虑跨平台差异"
source_pr: "NousResearch/hermes-agent#52917, NousResearch/hermes-agent#63970"
severity: medium
evidence:
  - "NousResearch #52917: 涉及桌面端"
  - "NousResearch #63970: 涉及桌面端"
learned_at: 2026-07-15
---

## 反模式说明

涉及桌面端的 PR 风险较高，因为桌面端和 Web 端有差异。

### 触发条件
- 修改桌面端 UI
- 修改桌面端功能
- 修改桌面端配置

### 如何避免
1. 测试桌面端兼容性
2. 提供桌面端特定测试
3. 考虑跨平台差异
