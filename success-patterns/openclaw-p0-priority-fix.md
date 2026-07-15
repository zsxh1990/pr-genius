---
type: Success Pattern
key: openclaw-p0-priority-fix
description: "OpenClaw P0 优先级修复 PR"
success_factors:
  - "P0 优先级标签"
  - "紧急修复"
  - "影响范围可控"
  - "包含测试"
repo_requirements:
  - "P0 标签"
  - "proof: sufficient"
source_pr: "openclaw/openclaw#104516, openclaw/openclaw#107063"
metrics:
  merge_rate: 0.90
learned_at: 2026-07-15
---

## 成功案例

### PR #104516: fix(config): reject zero-value resetArchiveRetention to prevent data loss

**成功因素**：
1. 标签包含 `P0` 优先级
2. 防止数据丢失的紧急修复
3. 影响范围可控

### PR #107063: fix(plugins): preserve state on npm metadata failures

**成功因素**：
1. 标签包含 `P0` 优先级
2. 防止插件状态丢失
3. 包含测试
