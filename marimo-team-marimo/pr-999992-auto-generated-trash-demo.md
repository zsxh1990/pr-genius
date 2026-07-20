---
type: PR Case Study
title: "auto-generated trash detection — ContribAI demo case"
description: "Demo case showing contribai-auto-generated-trash anti-pattern detection."
repo: marimo-team/marimo
pr_number: 999992
pr_url: https://github.com/marimo-team/marimo/pull/999992-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/marimo-team/marimo/pull/999992-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-auto-generated-trash.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- marimo-team
- auto-generated-trash
- v1.4.0
rounds:
- round: 1
  action: close
  delta:
    kind: code_change
    value: +89 / -12 / 4 files
    verified_at: '2026-07-19T20:30:00Z'
    confidence: high
  response_time_h: 0.5
  maintainer_action: closed — contains generated files
  bot_review: []
  blocker: null
  resolution: generated_artifacts
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: PR contains generated files
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-auto-generated-trash.md
---

# Auto-Generated Trash Detection

AI agent generated a PR with tool artifacts (README.md --- files).

## Fix Action

Check diff: `git diff --stat | grep "---"`
