---
type: Anti-Pattern
key: premature-fix-without-issue
description: "未经 Issue 讨论直接提交修复，且修复范围不明确"
symptom: "修复的问题未在 Issue 中确认，修复方案未经社区讨论，作者自行关闭"
trigger_keywords:
  - "explain why"
  - "rejected"
fix_action: "先开 Issue 确认问题存在且需要修复。修复 PR 应关联 Issue，并在 PR 描述中说明问题背景和修复方案"
source_pr: "BerriAI/litellm#36477"
severity: medium
evidence:
  - "BerriAI/litellm#36477: 作者 @yassin-berriai 自己关闭，无 maintainer 评论"
learned_at: 2026-08-11
---

## 反模式说明

**PR**: [BerriAI/litellm#36477](https://github.com/BerriAI/litellm/pull/36477)
**作者**: @yassin-berriai
**标签**: 无
**关闭原因**: 作者自己关闭

### PR 描述

修复 Bedrock 拒绝 Anthropic web_search 工具的问题，添加更清晰的错误信息。

### 关键特征

- 未在 Issue 中确认问题
- 修复方案未经社区讨论
- 作者自行关闭，可能意识到修复范围或方向问题
- 无 maintainer 反馈

### 如何避免

1. 先开 Issue 确认问题存在且需要修复
2. 在 Issue 中讨论修复方案
3. PR 描述中说明问题背景和修复思路
4. 关联 Issue (Fixes #NNN)

### 历史案例

- BerriAI/litellm#36477: 作者自行关闭
