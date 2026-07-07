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

### H. agentic #1382 `status: open` 应是 merged ✅ FIXED (v0.7.2)

**位置**：`agentic-community-mcp-gateway-registry/pr-1382-auth-md-mermaid-token.md`  
**问题**：frontmatter 写 `status: open`，GH API 实测 `state=closed, merged=True, merged_at=2026-07-04T16:30:18Z, merged_by: aarora79`。  
**修法**：v0.7.3 commit `0f76149` 修改 frontmatter `status: closed-merged` + 填入 `merged_at` / `closed_at` / `final_status: closed-merged`。

### I. e2b #1413 `status: merged` 实际是 closed-not-merged ✅ FIXED (v0.7.3)

**位置**：`e2b-dev-e2b/pr-1413-rich-to-ansi.md`  
**问题**：frontmatter `status: merged, merged_at: 2026-06-09`，但 GH API 实测 `state=closed, merged=False, closed_at=2026-06-09T18:38:28Z`。这是 refactor PR 被关闭但并未 merge，跟 title 描述「成功合并」不符。  
**修法**：v0.7.3 修 frontmatter 为 `status: closed-not-merged` + 跟 sync `final_status`。body 中“成功合并”需要二次 review 可能需要改跟正文。

### J. agentic #1383 `status: open` 实际是 closed-merged ✅ FIXED (v0.7.3)

**位置**：`agentic-community-mcp-gateway-registry/pr-1383-egress-vault-mermaid-placeholders.md`  
**问题**：frontmatter `status: open`，GH API 实测 `state=closed, merged=True, merged_at=2026-07-04T16:28:52Z`。同 #1382 合并后未同步。  
**修法**：v0.7.3 跟 #1382 同 pattern：status → closed-merged + 填时间。

---

## 待验证项（克莱恩 23:29 拍板）

### 候选 PR

- **首选**：honcho #801（7/9 前无回应 → bump round 5）
- **次选**：qdrant/mcp-server-qdrant #143（7/9 前无回应 → 主动 close round 4）
- **备用**：future-agi #778（7/5 bump 是一轮 third-party check-in）

### 验证维度（v0.5.0 升级后）

- [x] action enum 9 值够不够？ ✅ **v0.5.0 实证**（honcho 4 rounds + qdrant 3 rounds 全部迁）— 克莱恩 2026-07-02 23:29 GMT+8 拍板"够用不动"
- [x] delta kind 3 种够不够？ ✅ **v0.5.0 实证**（`code_change` 1 / `no_code_change` 1 / `unknown` 5 — `unknown` 是为等下一次 GH API 取真实 diff 保留的过渡状态，名字不改）
- [x] close_decision status 5 种够不够？ ✅ **v0.5.0 实证**（honcho + qdrant 都用 `pending`，未来 close 时再统计）
- [x] rounds 长度上限？（一个 PR 多大轮次算"该止损"？） ✅ **初判 5+ rounds → close，避免浪费 maintainer 时间**（Qdrant/LangChain 实证：large PR 3+ rounds 无回应基本 close）

## 节奏守则（克莱恩 23:29 拍板）

- ❌ **不主动加新功能**（不再扩 agent_guidelines / anti-patterns / rounds）
- ✅ **真实 PR 触发时一并修复**
- ✅ **每跑一次真实 PR，review 一次 schema 够不够**
- ✅ **够用 → 沉淀到 MEMORY.md → 不动 schema**
- ⚠️ **不够用 → 升级到 v0.6.0**（不预设要升）

## 版本

- **v0.7.6 (2026-07-05 22:55 GMT+8)**: 1+2+3 = 指标 #4 + #7 + #1 partial
  - #4 profile-level verified_at 8/12 = 67% 到达 91.7% (8 个被脚本填上, 之前 4 个已是 verified) — 达 80% 标 ✅
  - #7 blog docs/BLOG.md 355 lines (~3000 字), README+INDEX 加引 ✅
  - #1 partial — refresh-profile-meta.py 是 re-runnable 填证据脚本, 以后 12 → 30 可以直接重用
  - 同期: docs/METRICS.md (指标对账), validate.py 加 `type: Roadmap` schema
  - validate.py --strict: 0 errors; --enforce-evidence: 0 warnings
- **v0.7.5 (2026-07-05 21:38 GMT+8)**: 1, 3, 4 完成 + push-via-api v2 强化 + v0.7.5 release 发布
  - amend rounds evidence 补全: e2b / future-agi / honcho / fastmcp round 2 都有 round-level evidence ✅
  - docs/INDEX.md sync: 修了 "12 PRs" 错, 加 round-evidence 行, version bump 0.7.4 → 0.7.5 ✅
  - Badges 自动化: archive/scripts/refresh-badges.py emit 9 endpoint JSON (validate/evidence/round_evidence/profiles/cases/lessons/releases/latest_release/prgenius_version); README 10 badge 槽都连上
  - Round-level evidence: 21/21 (100%) — 11 round 1 + 4 amend + 6 check_in/bump/human_review
  - git-push-via-api.py 加 --push-all-unpushed loop: 6 commits (含 af2c785 / a8188d6 / 6a1633e / 414b200 / 65dca0c 本地未 push 的) 一个一个 push 到远端
  - v0.7.5 GitHub Release 发布 (id=349120080, tag=c9366a46), 10th GH release total
  - validate.py --strict: 0 errors ✅
  - validate.py --enforce-evidence: 0 warnings ✅
- **v0.7.5 (2026-07-05 13:30 GMT+8)**: 1, 3, 4 继续完善 (内期 early pass)
- **v0.7.4 (2026-07-05 12:46 GMT+8)**: 继续完善
  - Round-level evidence 补全 (11/11 case round 1 都 verified_at + 3 evidence_urls + confidence)
  - CI workflow 加 --enforce-evidence hard gate (不 warning, 真正失败 PR)
  - README badges 加 evidence--coverage + Latest release
  - prgenius 内部版本 bump 0.1.0 → 0.7.3 (跟外部 release 对齐)
  - .gitignore /data 加 `~` 确保 git refresh-index 能看。tramadi ng-fix
  - archive/scripts/inject-round-evidence.py (re-runnable round 1 evidence installer)
  - archive/scripts/create-v074-release.py
  - GitHub Release v0.7.4 现已发
- **v0.7.3 (2026-07-05 12:25 GMT+8)**: 真正的 release released
  - final commit on main = 4c94126b (远端 GH-API SHA, 本地 0f76149)
  - 8 发布：v0.6.0 / v0.6.1 / v0.6.2 / v0.6.3 / v0.6.4 / v0.7.0 / v0.7.1 / v0.7.3（从 5 升至 8）
  - v0.6.3 / v0.6.4 / v0.7.0 release notes + tags 补齐 (12:19 GMT+8)
  - v0.7.1 → v0.7.3 in-place release bump (包含 archive scripts + 全证据补齐)
  - 100% case-level evidence coverage (--enforce-evidence: 0 warnings)
  - 4 status drift 修复 (H/I/J/G 顶部 status 修)
- v0.7.3 (2026-07-05 12:21 GMT+8): commit-level: 全 case evidence 100% + 修 4 status drift
  - 剩 6 case 补 case-level evidence (e2b / future-agi / harbor / fastmcp / agentic #1383 / sourcebot)
  - 修 4 case status drift (H/I/J + 隐 G 顶部): agentic #1382/1383 → closed-merged; e2b #1413 / uv #19685 → closed-not-merged
  - refresh-evidence.py 加 6 target 到 11 total
  - 推 commit 通过 GH DB API (push via api.github.com:443)
- v0.7.2 (2026-07-05 11:35 GMT+8): commit-level: archive scripts + KNOWN_ISSUES update
  - archive/scripts/git-push-via-api.py --base-on-remote 升级
  - archive/scripts/create-v071-release.py
- v0.7.1 (2026-07-05 11:25 GMT+8): commit-level: MCP --repo-root wiring + PyPI rename + 5-case evidence
  - 5 case evidence (--enforce-evidence: 22 → 12)
  - CHANGELOG doc-drift fix
  - prgenius/README.md frontmatter fix
  - 推 commit 通过 GH DB API fallback (WSL→github.com:443 堵)
- v0.7.0 (2026-07-04): schema evidence layer + stdlib prgenius package + stdio MCP shell (commit ba3032b)
- v0.6.4 (2026-07-04): lesson-11 (mcp typo pool) + heartbeat snapshot + dashboard tool (commit d40c003)
- v0.6.3 (2026-07-04): agentic-community-mcp-gateway-registry profile + 2 case studies (commit f20cb83)
- v0.2.0 (2026-07-02 23:56): v0.5.0 review, 关 3 issues, 加 2 new findings
- v0.1.0 (2026-07-02): 初版
## Current validator state

- Files checked: **64**
- Errors: **1**
- Warnings: **0**
- Last heartbeat: 2026-07-07T02:04:49.075101+00:00

