---
type: Repo Profile
title: punkpeye/fastmcp PR 模式分析
description: FastMCP 仓 PR 模式 + zsxh1990 PR #282 进展
repo: punkpeye/fastmcp
url: https://github.com/punkpeye/fastmcp
star: 3239
language: TypeScript
zsxh_pr_count: 1
status: closed-282
analyzed_at: 2026-07-29
tags:
  - repo-profile
  - mcp
  - typescript
  - llm-testing
related:
  - ./pr-282-test-with-ollama.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: responsive
  bot_review: none
  ci_first_run_needs_approval: true  # 首提 PR 时 maintainer 需触发 CI
  default_branch: main
  response_time_h_median: 24
  merge_rate_30d: null
  close_keywords:
    - "prettier"
  one_pr_friendly: true
misakanet_queries:
  - misakanet/lessons/contrib/mcp-server-template.md  # MCP server 模板经验
misakanet_lessons: []
federation_status: declared-2026-07-02
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/punkpeye/fastmcp
  - https://api.github.com/repos/punkpeye/fastmcp
  - https://api.github.com/repos/punkpeye/fastmcp/releases/latest
  - https://api.github.com/repos/punkpeye/fastmcp/commits
confidence: high
last_release: v4.4.0
last_commit_sha: b170e78c
stars: 3239
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/punkpeye/fastmcp/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/punkpeye/fastmcp/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/punkpeye/fastmcp/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/punkpeye/fastmcp/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/punkpeye/fastmcp/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/punkpeye/fastmcp/pulls?q=is%3Apr+is%3Aclosed
---


# punkpeye/fastmcp

> FastMCP 是 TypeScript 实现的 Model Context Protocol 框架（[punkpeye](https://github.com/punkpeye) 主导）。  
> **AI 友好度**：高（punkpeye 个人维护，主动接纳 PR）。  
> **zsxh1990 PR 经验**：1 个 open（#282）。

---

## 1. 友好度画像

- ✅ punkpeye 个人维护（响应快，< 24h）
- ✅ 测试覆盖友好（jest + vitest）
- ✅ 大量外部贡献（fastmcp 是 MCP 生态早期）
- ⚠️ PR 多但 maintainer 时间有限

---

## 2. zsxh1990 PR 进展

### ❌ #282 [feat: add testWithOllama() for local LLM testing](https://github.com/punkpeye/fastmcp/pull/282)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-28 |
| 状态 | **CLOSED**（2026-07-24） |
| 结果 | 未 merge |

**教训**：PR 体量大（+271/-16），punkpeye 时间有限未 review。考虑拆分更小的 PR。

---

## 3. 提 PR 方向

### 🥇 Bug fix: npx fastmcp dev broken (#148)

- 已知 bug，用户报告，修复价值高
- 低竞争（issue 已存在 1 年+）

### 🥈 测试覆盖扩展

- 加 ArkType/Valibot tool 参数测试（参考 #293 已 merge 的模式）
- 加 OAuth proxy 测试（参考 #286）

### 🥉 Feature: configure default/optional tools (#192)

- 允许 server 配置哪些 tools 默认启用
- 功能性 feature，需要讨论设计

### 其他方向

- #160: custom HTTP routes alongside MCP endpoints
- #42: OpenAPI to MCP converter (TypeScript 版本)

---

## 4. SOP

| 维度 | fastmcp 特色 |
|---|---|
| CI | vitest + prettier + eslint |
| Review | punkpeye 本人（24h 内响应）|
| Release | Changesets 自动化 |
| 测试 | 必带 jest test |

---

## 5. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #282 案例深读](./pr-282-test-with-ollama.md)