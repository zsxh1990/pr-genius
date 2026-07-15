---
type: Anti-Pattern
key: nousresearch-tool-specific
description: "NousResearch PR 涉及特定工具问题"
symptom: "标签包含 tool/web, tool/tts, tool/delegate"
trigger_keywords:
  - "tool/web"
  - "tool/tts"
  - "tool/delegate"
fix_action: "1) 测试特定工具兼容性; 2) 提供工具特定测试; 3) 考虑跨工具差异"
source_pr: "NousResearch/hermes-agent#53149, NousResearch/hermes-agent#45522"
severity: medium
evidence:
  - "NousResearch #53149: 涉及 web 工具"
  - "NousResearch #45522: 涉及 TTS 工具"
learned_at: 2026-07-15
---

## 反模式说明

涉及特定工具的 PR 风险较高，因为不同工具可能有差异。

### 触发条件
- 修改特定工具的调用逻辑
- 修改特定工具的配置
- 修改特定工具的错误处理

### 如何避免
1. 测试特定工具兼容性
2. 提供工具特定测试
3. 考虑跨工具差异
