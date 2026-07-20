---
type: Repo Profile
title: qdrant/mcp-server-qdrant PR 模式分析
description: Qdrant MCP server PR 模式 + zsxh1990 PR #143 stale 状态
repo: qdrant/mcp-server-qdrant
url: https://github.com/qdrant/mcp-server-qdrant
star: 1448
language: Python
zsxh_pr_count: 1
status: stale-26d
analyzed_at: 2026-07-01
evidence_urls:
  - https://github.com/qdrant/mcp-server-qdrant
  - https://api.github.com/repos/qdrant/mcp-server-qdrant
  - https://api.github.com/repos/qdrant/mcp-server-qdrant/pulls/143
  - https://api.github.com/repos/qdrant/mcp-server-qdrant/issues/143/comments
  - ./pr-143-ollama-provider.md
confidence: high  # zsxh1990 PR #143 stale-26d, 3 rounds 已记录
verified_at: 2026-07-06
tags:
  - repo-profile
  - mcp
  - qdrant
  - ollama
  - stale
related:
  - ./pr-143-ollama-provider.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false  # 2026-07-02 GH API 核实: CONTRIBUTING.md 不存在，无 CLA 条款
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: slow  # 28 天无活动 + 1.5 天无 check-in 回应验证
  bot_review: none
  ci_first_run_needs_approval: false
  default_branch: master  # 实测 PR #143 base=master, ⚠️ 标准是 main
  response_time_h_median: 672  # 28 天 = 4 周 (远超原估 7 天)
  merge_rate_30d: null
  close_keywords: []
  one_pr_friendly: false  # 评审极慢 (MCP server 仓普遍现象)
verified_at: 2026-07-02
misakanet_queries:
  - misakanet/lessons/contrib/stale-pr-handling.md  # 26 天无活动 stale PR 处置策略
misakanet_lessons: []
federation_status: declared-2026-07-02
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/qdrant/mcp-server-qdrant/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/qdrant/mcp-server-qdrant/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/qdrant/mcp-server-qdrant/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/qdrant/mcp-server-qdrant/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/qdrant/mcp-server-qdrant/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/qdrant/mcp-server-qdrant/pulls?q=is%3Apr+is%3Aclosed
---

# qdrant/mcp-server-qdrant

> Qdrant 官方 MCP server（向量数据库 + LLM embedding）。  
> **AI 友好度**：中（Qdrant 公司是 AI infra 公司，主动迎 AI）。  
> **zsxh1990 PR 经验**：1 个 open（#143），**26 天无活动 = ⚠️ stale**。

---

## 1. 友好度画像

- ✅ Qdrant 是 AI infra 公司（自家产品欢迎 AI 集成）
- ⚠️ maintainer 数量少（1-2 人核心）
- ⚠️ 外部 PR 评审慢（参考 qdrant/client 仓惯例）

---

## 2. zsxh1990 PR 进展（⚠️ stale）

### 🟢 #143 [feat: add Ollama embedding provider for local models](https://github.com/qdrant/mcp-server-qdrant/pull/143)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-04 03:40 UTC（**27 天前**） |
| 最后活动 | 2026-06-04 03:40 UTC（**26 天无活动**） |
| 状态 | open |
| +76 / -0 / 4 files | 适中 |
| comments / reviews | 0 / 0 |

**问题**：完全无活动 = **PR 大概率已死**。

**风险**：
- Qdrant 可能已自己加了 Ollama provider
- Qdrant 可能换 base branch（base: master，标准是 main）
- 26 天 GitHub Actions 应已警告但未确认

---

## 3. 优先级行动项

**立即**：
- zsxh1990 发 check-in："Friendly ping — any feedback on this one? Happy to address."
- 同时检查 base branch 是否仍是 `master`

**3 天后无回应**：
- 主动 close（参考 OpenClaw §6.1 优雅退出）

**教训**：
- MCP server 仓 PR 评审普遍慢
- 必须 v1 就附详细测试 + screenshot（Qdrant 类公司重视可视化）
- Ollama integration 现在生态很多，**先看是否已有官方实现**

---

## 4. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #143 案例深读](./pr-143-ollama-provider.md)