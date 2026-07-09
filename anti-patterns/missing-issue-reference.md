---
type: Anti-Pattern
key: missing-issue-reference
description: "PR body 提到 'fix' 但没有关联具体的 Issue 编号"
symptom: "mentions fix but no issue number"
trigger_keywords:
  - "missing-issue-link"
fix_action: "1) 在 PR body 中添加 'Fixes #NNN' 或 'Closes #NNN'; 2) 如果没有对应 Issue，先创建 Issue 讨论方案; 3) 确保 Issue 编号格式正确（#数字）"
source_pr: "langchain-ai/langchain#38736, langchain-ai/langchain#38735"
severity: high
evidence:
  - "langchain #38736: body 提到 fix 但没有关联 Issue 编号，被标记 missing-issue-link"
  - "langchain #38735: 同上"
learned_at: 2026-07-09
---

## 反模式说明

PR body 中使用了 "fix"、"issue"、"closes" 等词汇，但没有使用标准的 Issue 关联语法（`Fixes #123`、`Closes #456`）。维护者会标记 `missing-issue-link` 标签。

### 触发条件

- PR body 包含 "fix"、"issue"、"closes" 等词
- 但没有 `#数字` 格式的 Issue 引用
- 维护者期望先有 Issue 讨论

### 为什么这是反模式

1. 维护者无法追踪问题来源
2. 缺乏上下文，review 困难
3. 可能重复已有 Issue 的讨论

### 如何避免

1. 使用标准语法：`Fixes #123`、`Closes #456`、`Resolves #789`
2. 如果没有对应 Issue，先创建 Issue
3. 确保 Issue 编号是目标仓库的有效编号
