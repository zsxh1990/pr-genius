---
type: Schema Reference
title: Known Issues
description: pr-genius 已知数据瑕疵（待真实 PR 触发时一并修复）
version: 0.2.0
created: 2026-07-02
updated: 2026-07-02
---

# Known Issues — v0.5.0 review

> 克莱恩 2026-07-02 23:29 GMT+8 拍板节奏：先用真实 PR 验证 rounds 字段，再扩。
> 2026-07-02 23:50 拍板 v0.5.0 schema 升级（基于 2 真实样本：honcho + qdrant）。
> 本文件列出**已知数据瑕疵**，下次真实 PR 触发时一并处理。

## ✅ v0.5.0 已修（关闭）

### 1. delta 字段裸 null 歧义

**原 issue**：`delta: null` 含义模糊（"无变更" vs "未测量"）  
**修复**：v0.5.0 升级为对象 `{kind, value}`，3 种 kind `code_change` / `no_code_change` / `unknown`  
**状态**：✅ **已修**（2026-07-02 v0.5.0 commit `a3e744c`）  
**影响**：honcho 4 rounds + qdrant 3 rounds 已迁

### 2. action 字符串无约束

**原 issue**：action 字段是自由字符串（如 `"second check-in (zsxh1990) + close decision pending"`）  
**修复**：v0.5.0 升级为 9 值枚举（`open`/`amend`/`bot_review`/`human_review`/`check_in`/`bump`/`close`/`merge`/`decision`）  
**状态**：✅ **已修**  
**影响**：所有迁移 case 的 action 现在是 enum 值

### 3. close 决策信息无结构

**原 issue**：close 类决策只能"塞进 action 字符串"或"野外字段"  
**修复**：v0.5.0 schema 化 `close_decision: {status, reason, decided_at, actor}` case-level 字段  
**状态**：✅ **已修**  
**影响**：honcho + qdrant 都有 `close_decision: {status: pending, reason: ..., actor: zsxh1990}`

---

## 🟡 v0.5.0 仍未修（保留）

### A. uv #19685 delta 真实值缺失

**位置**：`astral-sh-uv/pr-19685-sarif-audit.md` round 1  
**问题**：delta 写了 `unknown`（v0.5.0 正确），但**真实值未拉**  
**修法时机**：下次提 uv PR 时调 GH API 拉 PR #19685 真实 diff 补 `value: "+N / -M / K files"`，然后把 `kind` 从 `unknown` 改成 `code_change`  
**优先级**：低（语义已经准，只差真实数字）

### B. 6 未迁移 case 还在 warning 状态

**位置**：6 个 PR Case Study（uv #19685 / e2b #1413 / future-agi #778 / harbor #2121 / fastmcp #282 / sourcebot #1383）  
**问题**：action 字符串 + delta 裸 string 仍在用 v0.1 格式  
**修法时机**：克莱恩拍板时一次性迁移（用 `--strict` 跑 validate 看到 errors 后批量改）  
**优先级**：中（gate #5 明示"别全仓大迁移"，保持 warning 是预期）

### C. 8 PR Case Study 缺 `commit` SHA

**位置**：全部 8 个  
**问题**：除了 honcho #801 写了 `7ac3afe`，其他 7 个没 SHA  
**原因**：当时手头没 GitHub CLI 实时拉  
**修法时机**：下次有人维护 pr-genius 时一次性 `gh pr view --json commits` 补齐  
**优先级**：低

### D. E2B #1413 bot 名字核

**位置**：`e2b-dev-e2b/pr-1413-rich-to-ansi.md` round 1  
**bot**：`chatgpt-codex-connector[bot]`  
**问题**：body 写 bot 名字，没独立核  
**修法时机**：下次提 E2B PR 时调 `gh pr view 1413 --json reviews`  
**优先级**：低

---

## 🆕 v0.5.0 新发现（v0.4.1/2 闭环时发现）

### E. profile `response_time_h_median` 实测值偏差大

**位置**：`qdrant-mcp-server-qdrant/index.md`  
**问题**：profile 估 `response_time_h_median: 168`（7 天），实测 672（28 天）= **4 倍低估**  
**修法时机**：所有 profile 加 `verified_at: YYYY-MM-DD` 字段，闭环验证后更新；honcho + qdrant 已加，其它 6 仓下次闭环时加  
**优先级**：中（Agent 决策基于 profile，估错会引导错方向）

### F. profile 真实数据与文档脱节

**位置**：`qdrant-mcp-server-qdrant/index.md`（zsxh1990 first check-in @ 7/1 04:36 UTC 完全没记录）  
**问题**：body 写"26 天无活动"，实际 7/1 已经有 1 个 check-in  
**修法时机**：每个 PR 闭环时，先用 GH API 拉 comments 重写 case study body  
**优先级**：中

### G. uv #19685 `status: merged` drift

**位置**：`astral-sh-uv/pr-19685-sarif-audit.md`  
**问题**：frontmatter 写 `status: merged / merged_at: 2026-06-05`，GH API 实测 `state=closed, merged=False, closed_at=2026-06-05T14:43:54Z, merge_commit_sha=604822fb`，两者不一致。可能是当时被 squash/rebase 替换导致。原本状态要看 `merged = true ? "merged" : "closed-merged-or-not"`重新推导  
**修法时机**：下次提 uv PR 时调 GH API 拉 PR #19685 重新对齐 status/merged 字段  
**优先级**：中

### H. agentic #1382 `status: open` 应是 merged

**位置**：`agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md`  
**问题**：frontmatter 写 `status: open`，GH API 实测 `state=closed, merged=True, merged_at=2026-07-04T16:30:18Z, merged_by: aarora79`。7/4 16:30 后已合并，case study 未同步。  
**修法时机**：下次提 agentic-community PR 时同步拉 #1382 真实状态并升级 case status 为 `final_status: closed-merged`（v0.5.0 valid value）  
**优先级**：中

---

## 待验证项（克莱恩 23:29 拍板）

### 候选 PR

- **首选**：honcho #801（7/9 前无回应 → bump round 5）
- **次选**：qdrant/mcp-server-qdrant #143（7/9 前无回应 → 主动 close round 4）
- **备用**：future-agi #778（7/5 bump 是一轮 third-party check-in）

### 验证维度（v0.5.0 升级后）

- [ ] action enum 9 值够不够？
- [ ] delta kind 3 种够不够？
- [ ] close_decision status 5 种够不够？
- [ ] rounds 长度上限？（一个 PR 多大轮次算"该止损"？）

## 节奏守则（克莱恩 23:29 拍板）

- ❌ **不主动加新功能**（不再扩 agent_guidelines / anti-patterns / rounds）
- ✅ **真实 PR 触发时一并修复**
- ✅ **每跑一次真实 PR，review 一次 schema 够不够**
- ✅ **够用 → 沉淀到 MEMORY.md → 不动 schema**
- ⚠️ **不够用 → 升级到 v0.6.0**（不预设要升）

## 版本

- v0.7.1 (2026-07-05 09:09)：N1 补 evidence + 发现 2 case status drift
  - 5 case 补 case-level `verified_at / evidence_urls / confidence`（honcho #801 / qdrant #143 / uv #19685 / mongodb #1309 / agentic #1382）
  - `--enforce-evidence`：22 → 12 warnings（还差 e2b/future-agi/harbor/fastmcp/sourcebot/agentic-#1383 六个 case）
  - validate.py --strict：0 errors（绿）
  - Add issue G（uv #19685 status drift merged 实际 closed-not-merged）/ H（agentic #1382 status drift open 实际 merged）
- v0.2.0 (2026-07-02 23:56)：v0.5.0 review，关 3 issues，加 2 new findings
- v0.1.0 (2026-07-02)：初版
## Current validator state

- Files checked: **61**
- Errors: **0**
- Warnings: **0**
- Last heartbeat: 2026-07-05T02:02:33.830674+00:00

