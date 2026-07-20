---
type: PR Case Study
title: "archived repo detection — ContribAI demo case"
description: "Demo case showing contribai-archived-repo anti-pattern detection."
repo: pandas-dev/pandas
pr_number: 999991
pr_url: https://github.com/pandas-dev/pandas/pull/999991-demo
author: contribai-demo
final_status: close
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
- https://github.com/pandas-dev/pandas/pull/999991-demo
- https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-archived-repo.md
confidence: high
schema_version: rounds-v0.5.0
tags:
- pr-case-study
- demo
- contribai
- pandas-dev-pandas
- archived-repo
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
  maintainer_action: closed — repo archived
  bot_review: []
  blocker: null
  resolution: archived
  commit: null
  timestamp: '2026-07-19T20:30:00Z'
close_decision:
  status: close
  reason: Repository archived
  decided_at: '2026-07-19T20:30:00Z'
  actor: contribai-demo
links:
- type: anti-pattern
  target: anti-patterns/contribai-archived-repo.md
---

# Archived Repository Detection

Contributor submitted a PR to an archived repository.

## Fix Action

Check repo status: `gh repo view org/repo --json isArchived,isDisabled`
