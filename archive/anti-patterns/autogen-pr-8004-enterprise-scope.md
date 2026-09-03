---
type: Anti-Pattern
key: out-of-scope-enterprise-feature
description: "向开源项目提交企业级功能，超出项目范围"
symptom: "提交的功能与项目核心定位不符，过于企业化/商业化，无社区讨论"
trigger_keywords:
  - "enterprise"
  - "token cost"
  - "middleware"
fix_action: "先在 Issue 或 Discussion 中讨论功能是否符合项目范围。企业级功能可能更适合商业扩展或插件，而非核心代码"
source_pr: "microsoft/autogen#8004"
severity: medium
evidence:
  - "microsoft/autogen#8004: 作者 @glatinone 自己关闭，Co-authored-by: Copilot，无 maintainer 评论"
learned_at: 2026-08-11
---

## 反模式说明

**PR**: [microsoft/autogen#8004](https://github.com/microsoft/autogen/pull/8004)
**作者**: @glatinone (Co-authored-by: Copilot)
**标签**: 无
**关闭原因**: 作者自己关闭，可能意识到功能超出范围

### PR 描述

添加企业级 token 成本计算中间件，包含结构化 token 计数和费用估算。使用 Copilot 协作编写。

### 关键特征

- 功能过于企业化，与 autogen 核心定位不符
- 无 Issue 或 Discussion 先行讨论
- 使用 AI (Copilot) 协作编写，可能缺少对项目架构的深入理解
- 作者自行关闭，可能在提交后意识到范围问题

### 如何避免

1. 提交前先在 Issue/Discussion 中讨论功能是否符合项目范围
2. 企业级功能考虑作为插件或扩展，而非核心代码
3. 了解项目 roadmap 和贡献指南
4. AI 协作编写的代码需要人工审查和理解

### 历史案例

- microsoft/autogen#8004: 企业级功能，作者自行关闭
