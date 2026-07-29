---
type: Repo Profile
title: punkpeye/mcp-proxy PR 模式分析
description: TypeScript MCP proxy — stdio to HTTP/SSE bridge
repo: punkpeye/mcp-proxy
url: https://github.com/punkpeye/mcp-proxy
star: 272
language: TypeScript
zsxh_pr_count: 0
status: target
analyzed_at: 2026-07-29
tags:
  - repo-profile
  - mcp
  - typescript
  - proxy
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
  ci_first_run_needs_approval: true
  default_branch: main
  response_time_h_median: 24
  merge_rate_30d: null
  one_pr_friendly: true
confidence: medium
last_release: null
stars: 272
---

# punkpeye/mcp-proxy

> TypeScript 实现的 MCP 代理 — 将 stdio transport 转换为 HTTP/SSE。  
> **AI 友好度**：高（punkpeye 个人维护）。  
> **zsxh1990 PR 经验**：暂无。

---

## 1. 友好度画像

- ✅ punkpeye 个人维护（响应快，< 24h）
- ✅ 代码量小（单文件 proxy），适合小贡献
- ✅ 3 个 open issue，竞争低
- ⚠️ 功能性 issue 需理解 MCP transport 协议

---

## 2. Open Issues（贡献机会）

| Issue | 标题 | 难度 |
|-------|------|------|
| #71 | Tunnel: 404 | 中 |
| #20 | support for SSE to streamable http | 中 |
| #19 | Allow to proxy HTTP stream servers | 中 |

---

## 3. 提 PR 方向

### 🥇 SSE → Streamable HTTP 转换（#20）

- MCP 新协议支持 streamable HTTP，proxy 需要适配
- 高价值，punkpeye 会关注

### 🥈 测试覆盖

- 当前测试少，加 proxy 转发测试
- 低风险，易 merge

### 🥉 文档

- 加 "5 min quick start" 教程
- 加 Docker 使用说明

---

## 4. SOP

| 维度 | mcp-proxy 特色 |
|------|----------------|
| CI | vitest + prettier |
| Review | punkpeye 本人 |
| 测试 | 需要集成测试 |

---

## 5. 关联文档

- [fastmcp profile](../punkpeye-fastmcp/index.md)
