---
type: PR Case Study
title: fastmcp PR #282 - testWithOllama() for local LLM testing
description: zsxh1990 在 fastmcp 提的 Ollama 测试工具 PR，首次外部贡献等待 CI
pr_number: 282
pr_url: https://github.com/punkpeye/fastmcp/pull/282
repo: punkpeye/fastmcp
author: zsxh1990
status: open
opened_at: 2026-06-28
last_activity: 2026-06-28
tags:
  - pr-case-study
  - open
  - mcp
  - ollama
  - first-time-contributor
related:
  - ../index.md
rounds:
  - round: 1
    action: "open PR"
    delta: "+271 / -16 / 1 file"
    response_time_h: null  # 首次贡献，CI 未跑
    maintainer_action: null
    bot_review: []
    blocker: "CI 未跑（首次贡献需 maintainer 授权）"
    timestamp: "2026-06-28T08:13:00Z"
  - round: 2
    action: "amend (CI fix: prettier)"
    delta: "格式调整"
    response_time_h: 1.5
    maintainer_action: null
    bot_review: []
    blocker: "Prettier formatting issue"
    resolution: "Fixed prettier formatting"
    timestamp: "2026-06-28T09:39:00Z"
final_status: open
opened_at: "2026-06-28T08:13:00Z"
last_activity: "2026-06-28T09:39:00Z"
next_action: "等 punkpeye 授权 CI + 真实 review"
---

# fastmcp PR #282: feat: add testWithOllama() for local LLM testing

> zsxh1990 在 [punkpeye/fastmcp#282](https://github.com/punkpeye/fastmcp/pull/282) 的 Ollama 测试 PR。  
> **状态**：🟢 open（3 天）  
> **特殊**：首次外部贡献，等待 maintainer 授权 CI。

---

## PR 内容

**问题**：MCP server 测试需要真实 LLM，但用 OpenAI/Anthropic 太贵  
**方案**：`testWithOllama()` helper - 自动起本地 Ollama + 跑 prompt  
**规模**：+271 / -16 / 1 file

---

## 关键反馈

- 2026-06-28 09:39 zsxh1990 自报："Fixed the Prettier formatting issue. CI may need maintainer approval for first-time contributors."

**含义**：GitHub 对首次贡献者会阻止 CI 自动跑，需要 maintainer 点 "Approve and run"。

---

## 下一步

- ⚠️ 等 punkpeye 授权 CI
- ⚠️ 等真实 review
- 风险：fastmcp 后续可能加 Ollama 测试标准 → 我们的实现要主动兼容

---

## 关联文档

- [fastmcp 仓 Profile](../index.md)
- [OKF bundle 根入口](../index.md)