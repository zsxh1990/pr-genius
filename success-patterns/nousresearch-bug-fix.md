---
type: Success Pattern
key: nousresearch-bug-fix
description: "NousResearch bug 修复 PR"
success_factors:
  - "type/bug 标签"
  - "清晰的 bug 描述"
  - "包含测试"
  - "影响范围可控"
repo_requirements:
  - "type/bug 标签"
  - "P1/P2 优先级"
source_pr: "NousResearch/hermes-agent#64639, NousResearch/hermes-agent#63970"
metrics:
  merge_rate: 0.75
learned_at: 2026-07-15
---

## 成功案例

### PR #64639: fix(telegram): attach polling instrumentation without inspecting closed sessions

**成功因素**：
1. 标签包含 `type/bug`
2. 清晰的 bug 描述
3. 影响范围可控

### PR #63970: chore(desktop): upgrade @assistant-ui to 0.14 + use built-in voice picker

**成功因素**：
1. 标签包含 `type/refactor`
2. 依赖升级，风险较低
3. 包含测试
