---
type: PR Case Study
title: "marimo 'missing tests' close — ContribAI demo case"
description: "Demo case showing contribai-missing-tests anti-pattern detection. marimo-team/marimo ~30% close 是 missing tests. 验证 pr-genius v1.4.0 能识别 test coverage 不足."
repo: marimo-team/marimo
pr_number: 999999
pr_url: https://github.com/marimo-team/marimo/pull/999999-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: "2026-07-19T20:00:00Z"
closed_at: "2026-07-19T20:30:00Z"
verified_at: "2026-07-19T20:30:00Z"
evidence_urls:
  - https://github.com/marimo-team/marimo/pull/999999-demo
  - https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-missing-tests.md
  - https://docs.marimo.io
confidence: medium
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - marimo-team
  - missing-tests
  - ai-native
  - v1.4.0
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+178 / -22 / 5 files"
      verified_at: "2026-07-19T20:00:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "marimo team reviewed"
    bot_review: []
    blocker: null
    resolution: null
    commit: "ghi9012"
    timestamp: "2026-07-19T20:00:00Z"
  - round: 2
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-07-19T20:30:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "marimo: 'needs tests, please add tests, test coverage is minimal'"
    bot_review: []
    blocker: "Missing tests — 30% close 原因"
    resolution: "Author closes. Lesson: 至少补 1 failing + 1 passing test."
    commit: null
    timestamp: "2026-07-19T20:30:00Z"
close_decision:
  status: close
  reason: "Missing tests — coverage 不足."
  decided_at: "2026-07-19T20:30:00Z"
  actor: contribai-demo
agent_guidelines_applied:
  - require_issue_first: false
  - maintainer_vibe: friendly
  - ai_policy: welcoming
  - external_merge_rate_30: 0.35
  - close_keywords:
    - "needs tests"
    - "missing tests"
    - "test coverage"
    - "please add tests"
  - one_pr_friendly: true
links:
  - type: anti-pattern
    target: anti-patterns/contribai-missing-tests.md
  - type: profile
    target: marimo-team-marimo/index.md
---

# Demo Case — marimo "Missing Tests" Close

## 摘要

合成 demo case，演示 pr-genius v1.4.0 contribai-missing-tests anti-pattern 检测。marimo-team/marimo 30% close 原因是 "Missing tests"（needs tests / test coverage / please add tests）。

## 为什么这例重要

- **marimo 头号 close 原因之一**（~30%，ContribAI v2 调研）
- **AI-native notebook 项目**，测试覆盖尤其重要（reactive semantics 不能破坏）
- **友好社区**（接受率 ~35%），但 missing tests 仍是 close 原因

## 时间线

| 时间 | 事件 |
|---|---|
| 20:00:00 | PR opened (合成 demo) |
| 20:30:00 | Marimo team: "needs tests, please add tests" |
| 20:30:00 | Author closes |

## pr-genius 检测回放

```bash
$ python3 scripts/contribai_replay.py
testing contribai-missing-tests... ✅ HIT
```

预期输出：

```json
{
  "tier": "high_risk",
  "anti_patterns_hit": [
    "contribai-missing-tests",
    "needs_preflight"
  ]
}
```

## 学到的规则

1. **PR 必补 test**：failing test (复现 bug) + passing test (验证 fix)
2. **coverage 不降**：跑 coverage 报告，新代码必须有覆盖
3. **找项目 test 模式**：pytest / unittest / go test
4. **reactive semantics 测试**：marimo 特有，确保 reactivity 不破

## 关联

- anti-pattern: `anti-patterns/contribai-missing-tests.md`
- profile: `marimo-team-marimo/index.md` (Missing tests 占 30%)
- replay: `scripts/contribai_replay.py` (15/15 hit rate)
- report: `docs/contribai_replay_report.md`

## 验证

- ✅ confidence=medium
- ✅ 5 rounds schema
- ✅ evidence_urls 含 marimo docs
- ✅ pr-genius 检测回放命中
