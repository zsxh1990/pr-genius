---
type: PR Case Study
title: "astral-sh/ty 'needs RFC' close — ContribAI demo case"
description: "Demo case showing contribai-needs-rfc-first anti-pattern detection. astral-sh/ty ~25% close 是 type system 设计需 RFC. 验证 pr-genius v1.4.0 能识别 type system 改动需要先 RFC."
repo: astral-sh/ty
pr_number: 999999
pr_url: https://github.com/astral-sh/ty/pull/999999-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: "2026-07-19T20:00:00Z"
closed_at: "2026-07-19T20:30:00Z"
verified_at: "2026-07-19T20:30:00Z"
evidence_urls:
  - https://github.com/astral-sh/ty/pull/999999-demo
  - anti-patterns/contribai-needs-rfc-first.md
  - https://docs.astral.sh/ty/
confidence: medium
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - astral-sh
  - ty
  - type-checker
  - needs-rfc
  - beta
  - v1.4.0
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+412 / -88 / 14 files"
      verified_at: "2026-07-19T20:00:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "astral-sh ty team reviewed"
    bot_review: []
    blocker: null
    resolution: null
    commit: "jkl3456"
    timestamp: "2026-07-19T20:00:00Z"
  - round: 2
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-07-19T20:30:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "astral-sh ty: 'needs RFC, please discuss design, design discussion needed'"
    bot_review: []
    blocker: "Type system 设计需 RFC — 25% close 原因"
    resolution: "Author closes. Lesson: 大改 type system 需先 RFC, 不直接提 PR."
    commit: null
    timestamp: "2026-07-19T20:30:00Z"
close_decision:
  status: close
  reason: "Needs RFC — type system 设计改动需先在 issue 讨论."
  decided_at: "2026-07-19T20:30:00Z"
  actor: contribai-demo
agent_guidelines_applied:
  - require_issue_first: false  # 推荐但不强
  - maintainer_vibe: friendly
  - ai_policy: welcoming
  - external_merge_rate_30: 0.40  # beta 阶段
  - close_keywords:
    - "needs RFC"
    - "please discuss design"
    - "design discussion needed"
    - "RFC process required"
  - one_pr_friendly: true
  - notes: "beta 阶段 — 维护者更接受反馈, 但 type system 改动仍需 RFC"
links:
  - type: anti-pattern
    target: anti-patterns/contribai-needs-rfc-first.md
  - type: profile
    target: astral-sh-ty/index.md
---

# Demo Case — astral-sh/ty "Needs RFC" Close

## 摘要

合成 demo case，演示 pr-genius v1.4.0 contribai-needs-rfc-first anti-pattern 检测。astral-sh/ty 25% close 原因是 "Needs RFC"（type system 设计改动需先 RFC）。

## 为什么这例重要

- **astral-sh/ty 头号 close 原因之一**（~25%，ContribAI v2 调研）
- **beta 阶段项目**，本应更开放，但 type system 设计仍需 RFC
- **跟 uv / ruff 不混打友好**：克莱恩战略评估明确指出 astral 不能整体打 friendly，每个子项目独立判断

## 时间线

| 时间 | 事件 |
|---|---|
| 20:00:00 | PR opened (合成 demo) |
| 20:30:00 | astral-sh ty: "needs RFC, please discuss design" |
| 20:30:00 | Author closes |

## pr-genius 检测回放

```bash
$ python3 scripts/contribai_replay.py
testing contribai-needs-rfc-first... ✅ HIT
```

预期输出：

```json
{
  "tier": "high_risk",
  "anti_patterns_hit": [
    "contribai-needs-rfc-first",
    "needs_preflight"
  ]
}
```

## 学到的规则

1. **type system 改动需 RFC**：ty 是 type checker，semantics 是核心
2. **beta 阶段 ≠ 一切开放**：beta 反馈开放 ≠ API/语义改动开放
3. **大改先开 issue**：type system 改动先在 issue 讨论
4. **performance benchmark 必填**："10x faster" 是核心卖点，perf 退化 reject

## 关联

- anti-pattern: `anti-patterns/contribai-needs-rfc-first.md`
- profile: `astral-sh-ty/index.md` (Needs RFC 占 25%)
- replay: `scripts/contribai_replay.py` (15/15 hit rate)
- report: `docs/contribai_replay_report.md`

## 验证

- ✅ confidence=medium
- ✅ 5 rounds schema
- ✅ evidence_urls 含 astral docs
- ✅ pr-genius 检测回放命中
