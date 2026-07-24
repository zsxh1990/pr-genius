---
type: PR Case Study
title: "feat(examples): safeTok ↔ OpenClaw DM bridge — scope mismatch 1.5 小时被 close"
description: "ductapecode 提给 OpenClaw 的 safeTok (Nostr NIP-44) 桥接示例；rating: 🦪 silver shellfish / merge-risk: automation+security-boundary / 1.5 小时被 ClawSweeper 识别 scope 不匹配并关 PR。教训：产品边界类 close 不需要 maintainer 介入，ClawSweeper 自己就能 route 到 ClawHub。"
repo: openclaw/openclaw
pr_number: 96797
pr_url: https://github.com/openclaw/openclaw/pull/96797
author: ductapecode
final_status: closed-not-merged
opened_at: "2026-06-25T13:25:05Z"
closed_at: "2026-06-25T14:50:21Z"
verified_at: "2026-07-19T14:45:00Z"
evidence_urls:
  - https://github.com/openclaw/openclaw/pull/96797
  - https://github.com/openclaw/openclaw/pull/96797/files
  - https://api.github.com/repos/openclaw/openclaw/pulls/96797
  - https://github.com/openclaw/openclaw/pull/96797#issuecomment-4799934246
confidence: high
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - openclaw
  - safetok
  - nostr
  - nip44
  - examples-scope
  - clawhub
  - silver-shellfish
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+691 / -2 / 5 files"
      verified_at: "2026-06-25T13:25:05Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/96797
      confidence: high
    response_time_h: 0.05
    maintainer_action: null
    bot_review: ["github-actions[bot]: dependency graph guard cleared", "socket-security[bot]: no dependency changes"]
    blocker: null
    resolution: null
    commit: "b8a2f77c878"
    timestamp: "2026-06-25T13:25:05Z"
  - round: 2
    action: bot_review
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-25T13:38:47Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/96797#issuecomment-4799934246
      confidence: high
    response_time_h: 0.23
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: scope 不匹配 — 走 ClawHub/plugin path, 不是 OpenClaw core"]
    blocker: "merge-risk: automation + security-boundary; broken run instruction; 当前 OpenClaw 已有 Gateway + plugin seams"
    resolution: "ClawSweeper 推荐 ClawHub/plugin/community path, 不动 core"
    commit: null
    timestamp: "2026-06-25T13:38:47Z"
  - round: 3
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-25T14:50:21Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/96797
      confidence: high
    response_time_h: 1.4
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: applied proposed close, reason = belongs on ClawHub"]
    blocker: null
    resolution: "Close as ClawHub/plugin scope. ClawSweeper 自己关, 不等 maintainer."
    commit: null
    timestamp: "2026-06-25T14:50:21Z"
close_decision:
  status: close
  reason: "Scope 不匹配 — safeTok 桥接是有用的可选 Nostr 集成，但 OpenClaw 已有 Gateway + plugin seams，应当走 ClawHub/plugin/community path，不动 core。同时 PR 本身有 broken run instruction + 广 automation + security 关注。ClawSweeper 主动 close。"
  decided_at: "2026-06-25T14:50:21Z"
  actor: clawsweeper[bot]  # 注意：bot 主动 close, 无 maintainer 介入
agent_guidelines_applied:
  - allow_unsolicited_pr: true
  - require_signed_off: false
  - require_cla: false
  - require_issue_first: false  # 注: 本 PR 没走 issue-first 流程
  - ai_policy: welcoming  # CONTRIBUTING 友好
  - ai_assisted_disclosure: true
  - maintainer_vibe: strict
  - bot_review: clawsweeper
  - ci_first_run_needs_approval: false
  - default_branch: main
  - response_time_h_median: 240
  - merge_rate_30d: 0.27
  - close_keywords:
    - "belongs on ClawHub"
    - "plugin scope"
    - "merge-risk: automation"
    - "merge-risk: security-boundary"
  - one_pr_friendly: false
links:
  - type: contrast
    target: openclaw-openclaw/pr-93310-openclaw-error-handler.md
    note: "本例 = ClawSweeper 自己关 (#96797 1.4h, #93310 11d); 但同样 close, 路径不同 (scope route vs author self-close)"
  - type: contrast
    target: openclaw-openclaw/pr-92872-qqbot-scoped-media.md
    note: "本例无 maintainer 介入; #92872 有 vincentkoc 主动 close"
  - type: research
    target: research/openclaw-pr-knowledge/report.md
    anchor: "§5.3 ClawSweeper close pattern"
---

# PR #96797 — safeTok ↔ OpenClaw DM Bridge

## 摘要

ductapecode 提给 OpenClaw 的示例桥接：通过 Gateway WebSocket 把 [safeTok](https://safetok.me) 的 Nostr NIP-44 DMs 接到 OpenClaw assistant session。**+691/-2/5 files**、rating 🦪 silver shellfish、含截图 proof、production 部署。**1.5 小时内被 ClawSweeper 识别 scope 不匹配，主动 close**，推荐走 ClawHub/plugin/community path。

## 为什么这例重要

跟前两例形成 3 种 close 模式对比：

| PR | close 触发者 | 决策延迟 | 关闭原因 |
|---|---|---|---|
| #93310 | **作者**主动 close | 11 天 | 自己判断不可继续 |
| #92872 | **maintainer** 主动 close | 11 天 | vincentkoc 政策分流 |
| #96797 | **ClawSweeper** 自己 close | 1.4 小时 | scope 路由 |

**关键洞察**：OpenClaw 维护者已经把 **scope routing 决策**委托给 ClawSweeper bot。bot 评分不是筛选门槛，是 **决策代理**。

## 时间线

| 时间 | 事件 |
|---|---|
| 13:25:05 | 提 PR（v1: +691/-2/5 files, 含 screenshot proof）|
| 13:25:37 | github-actions[bot]: dependency graph guard cleared |
| 13:25:58 | socket-security[bot]: no dependency changes detected |
| 13:38:47 | ClawSweeper 深度 review: scope 不匹配 → ClawHub/plugin path |
| 14:50:21 | ClawSweeper 自己 close PR（reason = belongs on ClawHub）|
| **总耗时** | **1.42 小时** |

## PR 内容

### 解决的问题

1. 用 OpenClaw + Claude OAuth — 不用 Anthropic API key
2. 通过 Nostr NIP-44 DMs 跟 OpenClaw agent 通信

### 架构

```
safeTok user (Nostr NIP-44 DM)
    │
    ▼
bridge.mjs (gateway WebSocket + chat.send/chat.history)
    │
    ▼
OpenClaw session → assistant reply
    │
    ▼ (NIP-44 encrypted response)
safeTok user
```

### Proof 质量

- ✅ 截图：production OpenClaw 实例上完整 DM 流转
- ✅ Seen-event 去重（持久化到磁盘）
- ✅ 无 hardcoded secrets（env-var 配置）
- ✅ 7 commits + 完整 README
- ⚠️ silver shellfish（评分不高）— automation + security 关注

### ClawSweeper close 原文

> Thanks for the idea. I checked the current extension path, and this is a better fit for ClawHub.com than OpenClaw core.
>
> Close as ClawHub/plugin scope: the safeTok bridge is a useful optional Nostr integration, but current OpenClaw already has Gateway and plugin seams for this outside core, and the branch also carries a broken run instruction plus broad automation and security-review concerns.
>
> So I'm closing this as a scope-fit item for the plugin/community path.

**关键判断点**：
1. "current OpenClaw already has Gateway and plugin seams" = 现有架构已支持
2. "branch also carries a broken run instruction" = PR 本身有质量问题
3. "broad automation and security-review concerns" = automation + security 标签

**3 个理由任意 1 个都足以 close**。本例 3 个全占。

## 学到的规则

1. **bot 自己能 close PR** — 不需要 maintainer 介入，scope routing 决策已委托
2. **1.4 小时是 scope mismatch 的典型 close 时间** — 跟 maintainer policy close（11 天）形成鲜明对比
3. **Examples 目录 ≠ 扩展点** — `feat(examples)` 不等于 OpenClaw 接受所有 examples
4. **ClawHub/plugin 是 OpenClaw 的"分流出口"** — 拒绝 core PR 但推荐具体去处
5. **automation + security-boundary 双标签 = 极快 close** — 比单 security-boundary 还快

## 跟前两例的对比

### close 路径维度

```
作者主动 ─────► (无 maintainer)
                  │
                  ▼
             author self-close     #93310 (11d)

maintainer 主动 ─► ClawSweeper 评分 + 政策分流
                  │
                  ▼
             maintainer policy     #92872 (11d)

ClawSweeper 主动 ─► scope 路由
                  │
                  ▼
             bot scope close       #96797 (1.4h)
```

### 时间分布（OpenClaw 6 月样本 219 PR）

| close 延迟 | 占比 | 主要原因 |
|---|---|---|
| < 6h | ~15% | scope mismatch, duplicate, 自动 close |
| 1-7d | ~30% | bot 评分卡门限, author 主动 |
| > 7d | ~55% | maintainer 实际看过但没接, author 主动放弃 |

## 关联

- 对比：`openclaw-openclaw/pr-93310-openclaw-error-handler.md` (11d, author close)
- 对比：`openclaw-openclaw/pr-92872-qqbot-scoped-media.md` (11d, maintainer close)
- 研究：`research/openclaw-pr-knowledge/report.md` §5.3 ClawSweeper close pattern
- 分流出口：https://clawhub.ai/

## 验证

- ✅ 真实 GitHub PR URL
- ✅ 3 轮 rounds（v0.5.0 schema）
- ✅ 4 个 evidence_urls（含 ClawSweeper close 原文链接）
- ✅ close_decision + actor=clawsweeper[bot]
- ✅ 3-PR 对比表（close 触发者 × 延迟 × 原因）
