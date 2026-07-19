---
type: PR Case Study
title: "pandas 'out of scope' close — ContribAI demo case"
description: "Demo case showing contribai-out-of-scope anti-pattern detection. pandas-dev/pandas ~40% close 是 out of scope (跟 3.0 roadmap 不一致). 验证 pr-genius v1.4.0 能识别这种 close reason."
repo: pandas-dev/pandas
pr_number: 999999
pr_url: https://github.com/pandas-dev/pandas/pull/999999-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: "2026-07-19T20:00:00Z"
closed_at: "2026-07-19T20:30:00Z"
verified_at: "2026-07-19T20:30:00Z"
evidence_urls:
  - https://github.com/pandas-dev/pandas/pull/999999-demo
  - anti-patterns/contribai-out-of-scope.md
  - https://pandas.pydata.org/docs/development/roadmap.html
confidence: medium  # 合成 case 基于 ContribAI 实证
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - pandas-dev-pandas
  - out-of-scope
  - roadmap
  - v1.4.0
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+245 / -12 / 8 files"
      verified_at: "2026-07-19T20:00:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "pandas core team reviewed"
    bot_review: []
    blocker: null
    resolution: null
    commit: "def5678"
    timestamp: "2026-07-19T20:00:00Z"
  - round: 2
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-07-19T20:30:00Z"
      confidence: high
    response_time_h: 0.5
    maintainer_action: "pandas core: 'out of scope, not aligned with 3.0 roadmap'"
    bot_review: []
    blocker: "Out of scope — 跟 3.0 roadmap 不一致 (40% close 原因)"
    resolution: "Author closes. Lesson: 看 roadmap / 在 issue 先讨论."
    commit: null
    timestamp: "2026-07-19T20:30:00Z"
close_decision:
  status: close
  reason: "Out of scope — not aligned with pandas 3.0 roadmap."
  decided_at: "2026-07-19T20:30:00Z"
  actor: contribai-demo
agent_guidelines_applied:
  - require_issue_first: true  # 必须 maintainer triage 后才能提
  - maintainer_vibe: strict
  - ai_policy: conditional
  - external_merge_rate_30: 0.10
  - close_keywords:
    - "Out of scope"
    - "Not in roadmap"
    - "Off-topic"
    - "Not aligned with 3.0 roadmap"
  - one_pr_friendly: false
links:
  - type: anti-pattern
    target: anti-patterns/contribai-out-of-scope.md
  - type: profile
    target: pandas-dev-pandas/index.md
---

# Demo Case — pandas "Out of Scope" Close

## 摘要

合成 demo case，演示 pr-genius v1.4.0 contribai-out-of-scope anti-pattern 检测。pandas-dev/pandas 40% close 原因是 "Out of scope"（跟 3.0 roadmap 不一致 / not in roadmap）。

## 为什么这例重要

- **pandas 头号 close 原因**（~40%，ContribAI v2 调研）
- **响应慢**（14 天中位数 vs NousResearch 3 天）
- **CI 首次需 maintainer 触发**（流程长）
- **不是代码质量问题是路线决策**：维护者说 "我们不做这个方向"

## 时间线

| 时间 | 事件 |
|---|---|
| 20:00:00 | PR opened (合成 demo) |
| 20:30:00 | Pandas core: "out of scope, not aligned with 3.0 roadmap" |
| 20:30:00 | Author closes |

## pr-genius 检测回放

```bash
$ python3 scripts/contribai_replay.py
testing contribai-out-of-scope... ✅ HIT
```

预期输出：

```json
{
  "tier": "high_risk",
  "anti_patterns_hit": [
    "contribai-docs-pr-missing-quickstart",
    "contribai-out-of-scope",
    "first_contributor_large_repo"
  ]
}
```

## 学到的规则

1. **提 pandas PR 前看 3.0 roadmap**：https://pandas.pydata.org/docs/development/roadmap.html
2. **issue 区先问 maintainer**："would you accept a PR for <X>?"
3. **看最近 50-100 closed PR close 关键词分布**：pandas out-of-scope 占 40%
4. **避免 docs-only PR**：撞维护者已有规划 (10% close)

## 关联

- anti-pattern: `anti-patterns/contribai-out-of-scope.md`
- profile: `pandas-dev-pandas/index.md` (Out of scope 占 40%)
- replay: `scripts/contribai_replay.py` (15/15 hit rate)
- report: `docs/contribai_replay_report.md`

## 验证

- ✅ confidence=medium
- ✅ 5 rounds schema
- ✅ evidence_urls 含 pandas roadmap
- ✅ pr-genius 检测回放命中
