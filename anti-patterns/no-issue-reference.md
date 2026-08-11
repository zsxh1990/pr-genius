---
type: Anti-Pattern
key: no-issue-reference
description: "PR 未关联 Issue，维护者无法追溯背景"
symptom: "PR 提交后维护者询问背景、动机或关联的 Issue"
trigger_keywords:
  - "related issue"
  - "fixes #"
  - "closes #"
  - "resolves #"
fix_action: "在 PR body 中添加 Fixes #NNN 或 Closes #NNN 关联已有 Issue。如果没有 Issue，先开 Issue 讨论"
source_pr: ""
severity: medium
evidence:
  - "大多数项目要求 PR 关联 Issue"
  - "无 Issue 的 PR 缺乏上下文，审查效率低"
learned_at: 2026-08-11
---

## 反模式说明

**问题**: PR 未关联 Issue，缺乏背景和上下文

### 关键特征

- PR body 未包含 Fixes/Closes/Resolves
- 无 Issue 讨论记录
- 维护者需要额外询问背景
- 变更动机不明确

### 为什么被拒绝

1. **缺乏上下文**: 维护者不了解变更背景
2. **无法追溯**: 无法关联到需求或 bug 报告
3. **审查效率低**: 需要额外沟通确认
4. **自动化受限**: 无法自动关闭 Issue

### 如何避免

1. **先开 Issue**: 
   - 报告 bug → 先开 Issue 描述问题
   - 提功能 → 先开 Issue 讨论方案
2. **关联 PR**: 
   - 在 PR body 中添加 `Fixes #NNN`
   - 或 `Closes #NNN`
   - 或 `Resolves #NNN`
3. **提供上下文**:
   - 说明变更动机
   - 链接相关讨论
   - 引用相关文档

### 示例

```markdown
## Summary
Fixes #123

This PR fixes the timeout issue when connecting to the database.

## Changes
- Added connection pooling
- Increased timeout from 30s to 60s

## Testing
- Added unit test for connection pooling
- Verified fix with manual testing
```
