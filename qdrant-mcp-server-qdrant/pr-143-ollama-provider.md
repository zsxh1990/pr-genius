---
type: PR Case Study
title: qdrant MCP server PR #143 - Ollama embedding provider
description: zsxh1990 在 qdrant/mcp-server-qdrant 提的 Ollama provider PR，26 天 stale
pr_number: 143
pr_url: https://github.com/qdrant/mcp-server-qdrant/pull/143
repo: qdrant/mcp-server-qdrant
author: zsxh1990
status: open-stale
opened_at: 2026-06-04
last_activity: 2026-06-04
tags:
  - pr-case-study
  - stale
  - ollama
  - mcp
related:
  - ../index.md
---

# qdrant MCP server PR #143: feat: add Ollama embedding provider for local models

> zsxh1990 在 [qdrant/mcp-server-qdrant#143](https://github.com/qdrant/mcp-server-qdrant/pull/143) 的 Ollama provider PR。  
> **状态**：🟡 open stale（**26 天无活动**）  
> **风险**：高（很可能已死）。

---

## PR 内容

**问题**：qdrant MCP server 默认用 OpenAI embedding，本地用户需要 Ollama  
**方案**：新增 `OllamaEmbeddingProvider`，接 qdrant-client 的 embedding 接口  
**规模**：+76 / -0 / 4 files

---

## 风险评估

| 风险 | 概率 | 影响 |
|---|---|---|
| Qdrant 已合并等效实现 | 高 | PR 失去价值 |
| base branch 仍是 `master`（非 `main`） | 已确认 | 可能需 rebase |
| maintainer 忙 | 高 | 评审无限延后 |
| GitHub Actions bot 警告 | 应有 | 接近自动 close |

---

## 下一步

**立即（克莱恩批）**：
- 发 zsxh1990 check-in（如果是克莱恩授权的话）
- 或者直接 close + 复盘教训

**复盘教训**（无论 close/不 close）：
- MCP server 类 PR 评审普遍慢
- 提交前必须查 [qdrant-client 仓](https://github.com/qdrant/qdrant-client) 是否有等效 PR
- Ollama integration 生态已饱和

---

## 关联文档

- [qdrant-mcp-server-qdrant 仓 Profile](../index.md)
- [OpenClaw §6.1 7 天无活动优雅退出](../../../MEMORY.md)