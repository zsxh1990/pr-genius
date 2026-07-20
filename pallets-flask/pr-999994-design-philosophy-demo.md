---
type: PR Case Study
title: "design philosophy mismatch — ContribAI demo case"
description: "Demo case showing contribai-design-philosophy-mismatch anti-pattern detection."
repo: pallets/flask
pr_number: 999994
pr_url: https://github.com/pallets/flask/pull/999994-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/pallets/flask/pull/999994-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-design-philosophy-mismatch.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- pallets-flask
- design-philosophy
- v1.4.0
rounds:
- round: 1
  action: close
  delta:
    kind: code_change
    value: +567 / -89 / 12 files
    verified_at: '2026-07-19T20:30:00Z'
    confidence: high
  response_time_h: 4.0
  maintainer_action: closed — doesn't fit design philosophy
  bot_review: []
  blocker: null
  resolution: philosophy_mismatch
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: Doesn't align with project design philosophy
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-design-philosophy-mismatch.md
---

# Design Philosophy Mismatch

Contributor submitted a PR that conflicted with the project's design philosophy.

## Fix Action

Read ARCHITECTURE.md / DESIGN.md before contributing.
