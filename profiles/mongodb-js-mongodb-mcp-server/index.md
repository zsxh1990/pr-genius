---
type: Repo Profile
title: mongodb-js/mongodb-mcp-server PR 模式分析
description: MongoDB 官方 MCP server 仓 PR 模式 + zsxh1990 PR #1309 经验
repo: mongodb-js/mongodb-mcp-server
url: https://github.com/mongodb-js/mongodb-mcp-server
star: 1073
language: TypeScript
zsxh_pr_count: 1
status: in-flight
data_source: zsxh PR #1309
analyzed_at: 2026-07-03
evidence_urls:
  - https://github.com/mongodb-js/mongodb-mcp-server
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/releases/latest
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309
  - ./pr-1309-azure-readme-version.md
confidence: high  # zsxh1990 PR #1309 in-flight, 持续观察
verified_at: 2026-07-06
tags:
  - repo-profile
  - mcp
  - mongodb
  - typescript
  - azure-deploy
related:
  - ./pr-1309-azure-readme-version.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false  # 2026-07-03 GH API 核实: CLA.md 不存在，但实际由 MongoDB 内部流程处理（待验证）
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming  # 默认友好（无反 AI 信号，PR 模板存在）
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: responsive  # 80% merge rate + Jira-like 内部编号 = 团队节奏快
  bot_review: none
  ci_first_run_needs_approval: false  # fork PR 默认走外部 CI
  default_branch: main
  response_time_h_median: 48
  merge_rate_30d: 0.80  # 16/20 最近 20 closed PR
  close_keywords: []
  one_pr_friendly: true  # 1-file docs PR 友好
verified_at: 2026-07-03
misakanet_queries:
  - misakanet/lessons/contrib/ponytail-single-source-of-truth.md  # 删过期版本号，让 bicep 当 SSOT
misakanet_lessons: []
federation_status: declared-2026-07-03
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/mongodb-js/mongodb-mcp-server/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/mongodb-js/mongodb-mcp-server/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/mongodb-js/mongodb-mcp-server/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/mongodb-js/mongodb-mcp-server/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/mongodb-js/mongodb-mcp-server/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/mongodb-js/mongodb-mcp-server/pulls?q=is%3Apr+is%3Aclosed
---

# mongodb-js/mongodb-mcp-server

> MongoDB 官方 Model Context Protocol server（让 AI agent 操控 MongoDB Atlas + 本地 MongoDB cluster）。  
> **AI 友好度**：高（无反 AI 信号 + PR 模板规范 + 团队节奏快）。  
> **zsxh1990 PR 经验**：1 个 open（#1309），第一次 XS 探路。  
> **技术栈**：TypeScript / Node 20.19+ / 22.13+ / 24+（engines 已放松） / pnpm workspace。

---

## 1. 友好度画像

### 1.1 关键信号

| 维度 | 数据 | 评估 |
|---|---|---|
| 30d merge rate | 80% (16/20) | ✅ **极高**（比 OpenClaw 70.9% 还高） |
| 默认 branch | `main` | ✅ |
| 最近更新 | 5 小时前 | ✅ 极活跃 |
| CONTRIBUTING.md | ✅ 存在（11110 chars，详尽） | ✅ |
| PR 模板 | ✅ `.github/pull_request_template.md` | ✅ |
| CLA bot | ❌ 无 | ✅ 友好 |
| 反 AI 标签 | ❌ 0 个 | ✅ |
| 维护者响应 | Jira-like 编号 (MCP-57/MCP-572) | ✅ 团队有 sprint 节奏 |

### 1.2 友好度结论

- ✅ **开门型友好**：merge rate 80% + CONTRIBUTING 详尽 + PR 模板 + Jira 编号 = 团队对外 PR 真接受
- ✅ **无 anti-AI 信号**
- ⚠️ **不是 good-first-help-wanted 友好**（0 个标签）——小 PR 需自己找
- ⚠️ **TS 仓不是 Python**——PR diff 容易因 prettier/eslint 反复 amend
- ⚠️ **MongoDB 官方 = 内部流程多**（Jira 编号 + 关联 Jira）——非小 PR 可能需要等

---

## 2. zsxh1990 PR 进展

### 🟢 #1309 [docs(azure): remove stale tested image version](https://github.com/mongodb-js/mongodb-mcp-server/pull/1309)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-07-03 00:13 GMT+8 |
| 状态 | open, draft=False, merged=False |
| +1 / -1 / 1 file | **XS**（1 line change） |
| 上游 | mongodb-js/mongodb-mcp-server |
| 来自 fork | zsxh1990/mongodb-mcp-server |
| 验证 | 纯 docs，无 CI 触发需要 |

**关键信号**：
- ✅ Ponytail 守则："stdlib 有 → 用" 扩展为 "config 有 → 用"（bicep/main.bicep 当 SSOT）
- ✅ 不引入新版本号（避免下次又 stale）
- ✅ 文件改动 ≤ 3 lines = OpenClaw §6.1 #2 XS/S 友好 size
- ✅ 类型 TypeScript，**没有 lint/test 触发**（纯 docs，不动 .ts/.bicep）

---

## 3. 提 PR 方向

### 🥇 docs typo / version drift 类（已铺路）

- ✅ #1309：Azure deploy README 删 stale tested version
- 候选：README "Node.js" 多处不一致（v20 vs v22.13+）—— 但**这条更复杂**，需要确认 deprecation policy
- 候选：`api-extractor/reports/*.api.md` 自动生成，可能有过时 API 描述

### 🥈 small fix 类（待发现）

- 找 1-line chore 类 = `#1304 chore: remove classic CLI` 风格
- 优先 patch test name / comment（不动逻辑）

### 🚫 不要碰

- ❌ MCP protocol 行为改动
- ❌ auth/security 边界
- ❌ MongoDB 连接语义
- ❌ 大型 dependency upgrade
- ❌ Bicep 模板逻辑（只在 docs 范围）

---

## 4. SOP

### 🛠 提 PR 前 checklist

1. **读 CONTRIBUTING**（11110 chars 含代码风格 / 测试要求 / braintrust eval）
2. **fork 到 zsxh1990/**（无 push 权限到 upstream）
3. **用 fork branch 提 PR**（standard GitHub 工作流）
4. **PR title 用 conventional commits**：`<type>(<scope>): <subject>`
5. **PR body 精简**：Summary / Testing 两段即可
6. **不动 conventional files**：CONTRIBUTING 里链接"Agent Operating Principles"等

### 🤖 Agent 调用方式

```yaml
# Agent 拿到 mongodb-js/mongodb-mcp-server 决策时读这个 profile:
decision:
  - ai_policy: welcoming → 直接提 PR 不必 issue-first
  - one_pr_friendly: true → 小 PR 风险低
  - response_time_h_median: 48 → 期望 2 天回应
  - 80% merge rate → 期望乐观
  - maintainer_vibe: responsive → 不用 friendly check-in ping（除非 7 天+ 无活动）
```

---

## 5. MisakaNet 联邦

- `misakanet_queries`: 1 个路径
  - `ponytail-single-source-of-truth.md`——"删 stale 版本号让 bicep 当 SSOT" 是 Ponytail "stdlib 有就用" 的延伸原则
- `misakanet_lessons`: [] —— 本 PR 还没合并，无 lesson 吸收

---

## 关联文档

- [KNOWLEDGE_ISSUES / 黑名单](../BLACKLIST.md) — mongodb-js 不在拉黑清单
- [anti-patterns](../anti-patterns/) — 本仓无命中反模式
- [OKF bundle 根入口](../index.md)

## PR Case Studies（本仓 1 项）

- [pr-1309-azure-readme-version.md](./pr-1309-azure-readme-version.md) — mongodb-mcp-server #1309 — docs(azure): remove stale tested image version

---

## 📝 更新日志

### 2026-07-03 v0.1.0（初次建档）

- 建 profile 仓 `mongodb-js-mongodb-mcp-server/`
- agent_guidelines 17 字段填齐（CLA 待 PR 反馈验证）
- zsxh_pr_count: 1 (PR #1309 docs/remove stale version)
- MisakaNet 联邦声明就位
- 触发：克莱恩 2026-07-02 23:50 拍板 "mongodb-js 小 PR 探路"
