---
type: Schema Reference
title: Known Issues
description: pr-genius 已知数据瑕疵（待真实 PR 触发时一并修复）
version: 0.1.0
created: 2026-07-02
---

# Known Issues — v0.4.0 review 发现

> 克莱恩 2026-07-02 23:29 GMT+8 拍板：先用真实 PR 验证 rounds 字段，再扩。
> 本文件列出**已发现但不立即修**的数据瑕疵，下次真实 PR 触发时一并处理。

## v0.4.0 review 发现

### 1. uv #19685 delta 字段缺失

**位置**：`astral-sh-uv/pr-19685-sarif-audit.md` round 1  
**问题**：`delta: "未深读 (SARIF output 实现)"`  
**应该**：写 `null` 或真实 diff 数字（+N / -M / K files）  
**优先级**：低（不影响 rounds 字段的核心价值——保留攻防过程）  
**修法时机**：下次提 uv PR 时，调 GH API 拉 PR #19685 真实 diff 补上

### 2. harbor #2121 / fastmcp #282 delta 来源

**位置**：`harbor-framework-harbor/pr-2121-optional-deps.md` round 1  
**位置**：`punkpeye-fastmcp/pr-282-test-with-ollama.md` round 2  
**问题**：delta 数字（+57/-23/6 等）从 case study body "规模"字段抄，没用 GH API 二次验证  
**风险**：如果 case study body 当时记错了，rounds 就跟着错  
**修法时机**：下次提 harbor/fastmcp PR 时调 GH API 验证

### 3. 8 PR Case Study 缺 `commit` SHA

**位置**：全部 8 个  
**问题**：除了 honcho #801 写了 commit `7ac3afe`，其他 7 个没 SHA  
**原因**：当时手头没 GitHub CLI 实时拉，只能从 PR description 找  
**修法时机**：下次有人维护 pr-genius 时一次性调 `gh pr view --json commits` 补齐

### 4. E2B #1413 bot 名字核

**位置**：`e2b-dev-e2b/pr-1413-rich-to-ansi.md` round 1  
**bot**：`chatgpt-codex-connector[bot]`  
**问题**：body 写 "chatgpt-codex-connector[bot] 自动 review" — 但 case study body 是 PR description 来源，没独立核  
**风险**：bot 名字写错不影响 rounds 价值，但污染搜索关键词  
**修法时机**：下次提 E2B PR 时调 `gh pr view 1413 --json reviews`

## 待验证项（克莱恩要求的"用真实 PR 验证 rounds 够不够用"）

**目标**：跑 1-2 次真实 PR，更新 rounds 字段，看是否够用。

### 候选 PR

- **首选**：honcho #801（如果 maintainer 响应 → bump + 等回应是一轮新数据）
- **次选**：qdrant/mcp-server-qdrant #143（26 天 stale → 主动 close 是一轮"close"类样本）
- **备用**：future-agi #778（7/5 bump 是一轮 third-party check-in）

### 验证维度

- [ ] rounds 字段的 10 个字段（round/action/delta/...）是否够用？
- [ ] 缺什么字段？（猜测可能缺 `ci_status: pass/fail`）
- [ ] 多余字段？（猜测 `delta` 在某些 PR 不重要）
- [ ] 时间戳精度（ISO-8601 UTC vs 简写）？
- [ ] rounds 长度上限？（一个 PR 多大轮次算"该止损"？）

## 节奏守则（克莱恩 23:29 拍板）

- ❌ **不主动加新功能**（不再扩 agent_guidelines / anti-patterns / rounds）
- ✅ **真实 PR 触发时一并修复上述 issues**
- ✅ **每跑一次真实 PR，review 一次 rounds schema 够不够**
- ✅ **够用 → 沉淀到 MEMORY.md → 不动 schema**
- ⚠️ **不够用 → 升级到 v0.5.0**

## 版本

- v0.1.0 (2026-07-02)：初版