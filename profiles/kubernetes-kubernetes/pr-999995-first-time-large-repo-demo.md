---
type: PR Case Study
title: "first-time large repo contributor — ContribAI demo case"
description: "Demo case showing contribai-first-time-large-repo anti-pattern detection."
repo: kubernetes/kubernetes
pr_number: 999995
pr_url: https://github.com/kubernetes/kubernetes/pull/999995-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/kubernetes/kubernetes/pull/999995-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-first-time-large-repo.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- kubernetes
- first-time-large-repo
- v1.4.0
rounds:
- round: 1
  action: close
  delta:
    kind: code_change
    value: +890 / -234 / 15 files
    verified_at: '2026-07-19T20:30:00Z'
    confidence: high
  response_time_h: 48.0
  maintainer_action: closed — first contribution, discuss in issue first
  bot_review: []
  blocker: null
  resolution: trust_deficit
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: First-time contributor to large repo, needs to build trust
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-first-time-large-repo.md
---

# First-Time Large Repo Contributor

First-time contributor submitted a complex PR to Kubernetes without establishing trust.

## Fix Action

Build trust first: participate in issues for 2-4 weeks, start with simple fixes.
