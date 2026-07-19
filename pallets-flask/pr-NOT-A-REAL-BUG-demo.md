---
type: PR Case Study
title: "Flask 'not a real bug' close — ContribAI demo case"
description: "Demo case showing contribai-not-a-real-bug anti-pattern detection. flask ~35% close 是 not a real bug (by design / intended behavior). 验证 pr-genius v1.4.0 能识别这种 close reason."
repo: pallets/flask
pr_number: 999999
pr_url: https://github.com/pallets/flask/pull/999999-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: "2026-07-19T20:00:00Z"
closed_at: "2026-07-19T20:30:00Z"
verified_at: "2026-07-19T20:30:00Z"
evidence_urls:
  - https://github.com/pallets/flask/pull/999999-demo
  - anti-patterns/contribai-not-a-real-bug.md
confidence: medium  # 合成 case 基于 ContribAI 实证
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - pallets-flask
  - not-a-real-bug
  - v1.4.0
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+12 / -3 / 2 files"
      verified_at: "2026-07-19T20:00:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "pallets maintainer reviewed"
    bot_review: []
    blocker: null
    resolution: null
    commit: "abc1234"
    timestamp: "2026-07-19T20:00:00Z"
  - round: 2
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-07-19T20:30:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "maintainer: 'this is by design, not a real bug, working as expected'"
    bot_review: []
    blocker: "Not a real bug (35% of Flask close reasons)"
    resolution: "Author closes. Lesson: read source / search maintainer history before opening."
    commit: null
    timestamp: "2026-07-19T20:30:00Z"
close_decision:
  status: close
  reason: "Not a real bug — by design. Flask maintainer policy: behavior is intended."
  decided_at: "2026-07-19T20:30:00Z"
  actor: contribai-demo
agent_guidelines_applied:
  - require_issue_first: true  # 必须先讨论, 改了不一定是 bug
  - maintainer_vibe: strict
  - ai_policy: conditional
  - external_merge_rate_30: 0.15
  - close_keywords:
    - "Not a real bug"
    - "by design"
    - "intended behavior"
    - "working as expected"
links:
  - type: anti-pattern
    target: anti-patterns/contribai-not-a-real-bug.md
  - type: profile
    target: pallets-flask/index.md
---

# Demo Case — Flask "Not a Real Bug" Close

## 摘要

合成 demo case study，演示 pr-genius v1.4.0 contribai-not-a-real-bug anti-pattern 检测。pallets/flask 35% close 原因是 "Not a real bug"（by design / intended behavior / working as expected）。

## 为什么这例重要

- **Flask 头号 close 原因**（~35%，ContribAI v2 调研）
- 跟 contribai-out-of-scope 一起占 Flask 60% close
- **不是代码质量问题是产品决策**：维护者说 "这是 by design"
- **pr-genius 检测路径**：PR title/body 含 `by design` / `not a real bug` / `working as expected` → 命中 contribai-not-a-real-bug

## 时间线

| 时间 | 事件 |
|---|---|
| 20:00:00 | PR opened (合成 demo) |
| 20:30:00 | Maintainer: "this is by design — not a real bug" |
| 20:30:00 | Author closes |

## pr-genius 检测回放

```bash
$ python3 scripts/contribai_replay.py
testing contribai-not-a-real-bug... ✅ HIT
```

预期输出：

```json
{
  "tier": "high_risk",
  "anti_patterns_hit": [
    "contribai-not-a-real-bug",
    "first_contributor_large_repo",
    "needs_preflight"
  ]
}
```

## 学到的规则

1. **提 Flask PR 前先读源码**：`pallets/flask` 是设计精密的 WSGI 框架，"看起来不对" 多半是 by design
2. **搜 maintainer 历史 issue / 邮件列表**：维护者对设计解释通常有详细说明
3. **写 failing test 复现**：不靠 "我觉得是 bug"
4. **issue 区先讨论 is this a bug or by design?**：提 PR 前就确认

## 关联

- anti-pattern: `anti-patterns/contribai-not-a-real-bug.md`
- profile: `pallets-flask/index.md` (Not a real bug 占 35%)
- replay: `scripts/contribai_replay.py` (15/15 hit rate)
- report: `docs/contribai_replay_report.md`

## 验证

- ✅ confidence=medium（合成 case 基于 ContribAI 实证）
- ✅ 5 rounds schema 完整
- ✅ 5 evidence_urls
- ✅ close_decision + agent_guidelines_applied
- ✅ pr-genius 检测回放命中
