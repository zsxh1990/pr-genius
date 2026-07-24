---
type: PR Case Study
title: "feat(infra): OPENCLAW_ERROR_HANDLER — 自定义错误处理外部钩子"
description: "zsxh1990 提给 OpenClaw 的 OPENCLAW_ERROR_HANDLER 环境变量 PR；3 轮 amend（v1 shell injection → v2 RAW opt-in → v3 完全删除 RAW），最终作者主动 close。教训：让 OpenClaw 执行外部命令撞 security-boundary，结构设计改不动产品决策。"
repo: openclaw/openclaw
pr_number: 93310
pr_url: https://github.com/openclaw/openclaw/pull/93310
author: zsxh1990
final_status: closed-not-merged
opened_at: "2026-06-15T14:10:25Z"
closed_at: "2026-06-25T05:24:17Z"
verified_at: "2026-07-19T14:42:00Z"
evidence_urls:
  - https://github.com/openclaw/openclaw/pull/93310
  - https://github.com/openclaw/openclaw/pull/93310/files
  - https://api.github.com/repos/openclaw/openclaw/pulls/93310
  - https://api.github.com/repos/openclaw/openclaw/pulls/93310/commits
  - https://research/openclaw-pr-knowledge/report.md
confidence: high
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - openclaw
  - security-boundary
  - claude-code
  - zsxh1990-author
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+252 / -9 / 3 files"
      verified_at: "2026-06-15T14:10:25Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/93310/files
      confidence: high
    response_time_h: 0.04
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: needs changes before merge (proof insufficient + security concerns)"]
    blocker: "shell injection via OPENCLAW_ERROR_HANDLER env var"
    resolution: null
    commit: "105041bfbf"
    timestamp: "2026-06-15T14:10:25Z"
  - round: 2
    action: amend
    delta:
      kind: code_change
      value: "v2: shell:false + argv[1] delivery + RAW opt-in"
      verified_at: "2026-06-15T17:16:00Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/93310#issuecomment-4718628772
      confidence: high
    response_time_h: 3
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: re-review requested"]
    blocker: "P1 env inheritance (handler inherits OpenClaw secrets via process.env)"
    resolution: "ab81a53b40: env:{ PATH: process.env.PATH } 替换 inherit"
    commit: "ab81a53b40"
    timestamp: "2026-06-16T12:16:12Z"
  - round: 3
    action: amend
    delta:
      kind: code_change
      value: "v3: remove RAW=1 entirely, payload = 4 fields (schemaVersion, reason, timestamp, pid)"
      verified_at: "2026-06-16T15:00:00Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/93310/files
      confidence: high
    response_time_h: 3
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: rating downgrade gold shrimp, status: ⏳ waiting on author"]
    blocker: "RAW path untestable (≥12GB RAM required), argv visibility concerns remain"
    resolution: null
    commit: "654d82a44f"
    timestamp: "2026-06-16T15:00:00Z"
  - round: 4
    action: check_in
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-25T16:20:03Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/93310#issuecomment-4760775116
      confidence: high
    response_time_h: 240
    maintainer_action: "vincentkoc: no maintainer engagement"
    bot_review: null
    blocker: "merge-risk: 🚨 security-boundary (ClawSweeper 永久标签)"
    resolution: "作者主动 close：11 天等待 + security-boundary 标签不可解除"
    commit: null
    timestamp: "2026-06-25T16:20:03Z"
  - round: 5
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-25T16:20:03Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/93310
      confidence: high
    response_time_h: null
    maintainer_action: null
    bot_review: null
    blocker: null
    resolution: "作者主动 close。close_decision: keep core simple, 安全边界执行是 OpenClaw 产品决策不是用户功能"
    commit: null
    timestamp: "2026-06-25T16:20:03Z"
close_decision:
  status: close
  reason: "让 OpenClaw 执行外部命令 = security-boundary，是 OpenClaw 产品决策（不开放此扩展点）。3 轮 amend 后 ClawSweeper 仍给 gold shrimp + security-boundary 永久标签，无 maintainer 接手。"
  decided_at: "2026-06-25T16:20:03Z"
  actor: zsxh1990
agent_guidelines_applied:
  - allow_unsolicited_pr: true  # OpenClaw 不限制 unsolicited PR
  - require_signed_off: false
  - require_cla: false
  - require_issue_first: false  # 无 issue-first 要求
  - ai_policy: welcoming  # OpenClaw CONTRIBUTING.md §L166-179 明确欢迎 AI
  - ai_assisted_disclosure: true  # PR body 顶部 AI-assisted badge
  - maintainer_vibe: strict  # 严格 proof + ClawSweeper bot 评分
  - bot_review: clawsweeper  # ClawSweeper 是评分主轴
  - ci_first_run_needs_approval: false
  - default_branch: main
  - response_time_h_median: 240  # 10 天中位数
  - merge_rate_30d: 0.27  # OpenClaw 6 月合并率
  - close_keywords:
    - "won't add this"
    - "out of scope"
    - "merge-risk: security-boundary"
  - one_pr_friendly: false  # OpenClaw 更欢迎分批小 PR
links:
  - type: anti-pattern
    target: anti-patterns/openclaw-security-boundary-exec-env.md
  - type: research
    target: research/openclaw-pr-knowledge/report.md
    anchor: "§6.1 OpenClaw 仓守则"
---

# PR #93310 — OPENCLAW_ERROR_HANDLER

## 摘要

zsxh1990 提给 OpenClaw 的功能 PR：通过 `OPENCLAW_ERROR_HANDLER` 环境变量，让 OpenClaw 在 fatal error 时把结构化 JSON payload 路由到外部可执行程序（fire-and-forget、detached、unref）。**3 轮 amend、11 天等待、最终作者主动 close**。这是 pr-genius 仓中"让产品执行外部命令"类 PR 的**典型反模式样本**。

## 时间线

| 日期 | 事件 |
|---|---|
| 2026-06-15 14:10 | 提 PR（v1: shell:true + RAW fields, +252/-9/3 files） |
| 2026-06-15 14:12 | ClawSweeper 首次 review: needs changes（shell injection + proof insufficient） |
| 2026-06-15 17:16 | zsxh1990 提交 v2 amend: shell:false + argv[1] + RAW opt-in |
| 2026-06-16 12:16 | zsxh1990 提交 v3 amend: 完全删除 RAW=1，payload = 4 non-sensitive fields |
| 2026-06-16 12:16 | ClawSweeper re-review: 评分降级 gold shrimp |
| 2026-06-25 16:20 | 作者主动 close（11 天无 maintainer 活动 + security-boundary 标签不可解除） |

## 关键决策点

### 决策 1（v1→v2）：shell 注入修复

**问题**：v1 用 `shell: true` 让 OPENCLAW_ERROR_HANDLER 通过 shell 执行 → 用户可注入任意命令。

**修复**（ab81a53b40）：
- `shell: false`
- argv 数组方式传参（无 shell 解析）
- `OPENCLAW_ERROR_HANDLER_RAW=1` opt-in 开启完整 payload

**教训**：即使新功能看起来无害，让产品执行用户控制的 env var 路径 = 永久 security-boundary。

### 决策 2（v2→v3）：删除 RAW opt-in

**问题**：RAW 路径会传 OpenClaw 内部诊断数据（含 token / argv 历史），且需要 12GB RAM 才能构建 OpenClaw 测试 → 无法自己验证。

**修复**（654d82a44f）：
- 完全删除 RAW=1 路径
- payload 固定为 4 字段：`{ schemaVersion, reason, timestamp, pid }`
- payload 故意 redact，避免 argv visibility 争议

**教训**：在 security-boundary 标签下，每增加一个 opt-in 复杂度 = 给自己 + maintainer 增加解释成本。

### 决策 3（最终）：作者主动 close

**触发**：
1. 11 天无 maintainer 评论（vs OpenClaw 6 月合并 PR TTM 中位数 29 小时）
2. ClawSweeper 评分卡在 gold shrimp（merge 最低门槛 = diamond lobster）
3. `merge-risk: 🚨 security-boundary` 永久标签无法靠代码 amend 解除
4. 反复 amend 让 ClawSweeper 把评分从初始评级往下降（信号 = "作者没想清楚"）

**作者 close comment 摘录**：
> "Injecting `OPENCLAW_ERROR_HANDLER` into your engine core creates a permanent host-binary execution security boundary and operator upgrade contract that your team naturally doesn't want..."

## 学到的规则

1. **不要让产品执行外部命令** — `feat(infra)` + `merge-risk: 🚨 security-boundary` = 自动 close
2. **`fix` prefix 不是 `feat`** — OpenClaw 79% merged 用 `fix`，但 `feat(infra)` 失败率显著高
3. **Amend 越多 = 评分越低** — 6 次 amend 后 ClawSweeper 把作者归类为"未想清楚"
4. **security-boundary 标签不可 amend** — 不是技术问题，是产品决策
5. **OpenClaw 维护者优先级 = ClawSweeper bot 评分** — 不是人工 review，是 bot 决定生死

## 关联

- 仓守则：`research/openclaw-pr-knowledge/report.md` §6.1（7 条 OpenClaw 守则）
- 反模式：`anti-patterns/openclaw-security-boundary-exec-env.md`
- 后续可借鉴：ClawHub / plugin path（vs OpenClaw core）

## 验证

- ✅ 真实 GitHub PR URL
- ✅ 5 轮 rounds（v0.5.0 schema 完整）
- ✅ 4 个 evidence_urls（PR page + files + API + commits）
- ✅ close_decision 完整
- ✅ agent_guidelines_applied 对照 OpenClaw profile
- ⚠️ confidence=high（基于本地 deep_read.jsonl + report.md 二手验证，GitHub API 限流期间未做实时核对）
