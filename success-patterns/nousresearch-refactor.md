---type: Success Pattern
key: nousresearch-refactor
tags: [cron, scheduling, reliability]
description: "NousResearch 重构 PR"
success_factors:
  - "type/refactor 标签"
  - "依赖升级"
  - "风险较低"
  - "包含测试"
repo_requirements:
  - "type/refactor 标签"
  - "P2/P3 优先级"
source_pr: "NousResearch/hermes-agent#63970, NousResearch/hermes-agent#107066"
metrics:
  merge_rate: 0.80
created: 2026-07-15
learned_at: 2026-07-15
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/nousresearch-refactor.md
updated: 2026-08-01
confidence: medium
---

## Pattern

### PR #63970: chore(desktop): upgrade @assistant-ui to 0.14 + use built-in voice picker

**成功因素**：
1. 标签包含 `type/refactor`
2. 依赖升级，风险较低
3. 包含测试

### PR #107066: refactor(whatsapp): let SDK own inbound command context

**成功因素**：
1. 标签包含 `type/refactor`
2. 代码重构，不改变功能
3. 提高代码可维护性

## Applicability

All repository sizes.
