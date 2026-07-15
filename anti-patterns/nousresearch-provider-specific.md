---
type: Anti-Pattern
key: nousresearch-provider-specific
description: "NousResearch PR 涉及特定 provider 问题"
symptom: "标签包含 provider/openai, provider/anthropic, provider/gemini"
trigger_keywords:
  - "provider/openai"
  - "provider/anthropic"
  - "provider/gemini"
fix_action: "1) 测试特定 provider 兼容性; 2) 提供 provider 特定测试; 3) 考虑跨 provider 差异"
source_pr: "NousResearch/hermes-agent#52865, NousResearch/hermes-agent#52866"
severity: medium
evidence:
  - "NousResearch #52865: 涉及 Google AI Studio provider"
  - "NousResearch #52866: 涉及 Gemini provider"
learned_at: 2026-07-15
---

## 反模式说明

涉及特定 AI provider 的 PR 风险较高，因为不同 provider 有差异。

### 触发条件
- 修改特定 provider 的认证逻辑
- 修改特定 provider 的 API 调用
- 修改特定 provider 的错误处理

### 如何避免
1. 测试特定 provider 兼容性
2. 提供 provider 特定测试
3. 考虑跨 provider 差异
