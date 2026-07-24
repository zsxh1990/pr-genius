---
type: PR Case Study
title: "duplicate PR detection — ContribAI demo case"
description: "Demo case showing contribai-duplicate-pr anti-pattern detection."
repo: pallets/flask
pr_number: 999990
pr_url: https://github.com/pallets/flask/pull/999990-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/pallets/flask/pull/999990-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-duplicate-pr.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- pallets-flask
- duplicate-pr
- v1.4.0
rounds:
- round: 1
  action: close
  delta:
    kind: no_code_change
    value: null
    verified_at: '2026-07-19T20:30:00Z'
    confidence: high
  response_time_h: 0.5
  maintainer_action: closed as duplicate of #4521
  bot_review: []
  blocker: null
  resolution: duplicate
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: Already fixed in #4521
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-duplicate-pr.md
---

# Duplicate PR Detection

Contributor submitted a PR to fix session cookie handling on redirect, but the same fix was already merged in PR #4521.

## Fix Action

Search before submitting: `gh search prs --repo org/repo --state all "<keyword>"`
