---
type: PR Case Study
title: "breaking change detection — ContribAI demo case"
description: "Demo case showing contribai-breaking-change-no-migration anti-pattern detection."
repo: astral-sh/ty
pr_number: 999993
pr_url: https://github.com/astral-sh/ty/pull/999993-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/astral-sh/ty/pull/999993-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-breaking-change-no-migration.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- astral-sh-ty
- breaking-change
- v1.4.0
rounds:
- round: 1
  action: close
  delta:
    kind: code_change
    value: +312 / -156 / 8 files
    verified_at: '2026-07-19T20:30:00Z'
    confidence: high
  response_time_h: 2.0
  maintainer_action: closed — breaking change without migration
  bot_review: []
  blocker: null
  resolution: breaking_change
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: Breaking change without migration path
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-breaking-change-no-migration.md
---

# Breaking Change Detection

Contributor submitted a breaking change PR without migration path.

## Fix Action

Provide migration path, feature flag, or deprecation cycle.
