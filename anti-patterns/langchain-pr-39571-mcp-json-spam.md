---
type: Anti-Pattern
key: spam-mcp-json-multiple-repos
description: "同一作者向多个仓库提交相同的 .mcp.json 配置文件"
symptom: "向多个无关仓库提交相同内容的 PR，无实质性代码贡献，属于垃圾内容/spam"
trigger_keywords:
  - "mcp.json"
  - "productivity-suite"
fix_action: "不要向多个仓库提交相同的配置文件。每个仓库的 PR 应该针对该仓库的具体需求，且必须先开 Issue 讨论"
source_pr: "langchain-ai/langchain#39571"
severity: high
evidence:
  - "langchain-ai/langchain#39571: missing-issue-link 标签，作者 @zellkernel 同时向 autogen#8038, litellm#36476 提交相同 PR"
  - "microsoft/autogen#8038: 作者自己关闭"
  - "BerriAI/litellm#36476: 作者自己关闭"
learned_at: 2026-08-11
---

## 反模式说明

**PR**: [langchain-ai/langchain#39571](https://github.com/langchain-ai/langchain/pull/39571)
**作者**: @zellkernel
**标签**: external, size: XS, missing-issue-link, new-contributor
**关闭原因**: 缺少 Issue 关联 + spam 行为

### PR 描述

向仓库添加 `.mcp.json` 配置文件，注册外部 MCP server。同一作者同时向 autogen#8038、litellm#36476、langchain#39571 提交了几乎相同的内容。

### 关键特征

- 无 Issue 关联（missing-issue-link 标签）
- 同一内容批量提交到多个仓库
- 配置指向外部服务 (render.com)，无安全审查
- 无实质性代码贡献

### 如何避免

1. 每个 PR 必须先开 Issue 讨论
2. 不要向多个仓库批量提交相同内容
3. 添加外部服务配置需要安全审查
4. PR 应该针对仓库的具体需求，而非通用模板

### 历史案例

- langchain-ai/langchain#39571: missing-issue-link，作者自行关闭
- microsoft/autogen#8038: 作者自行关闭
- BerriAI/litellm#36476: 作者自行关闭
