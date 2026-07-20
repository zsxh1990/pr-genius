---
type: PR Case Study
title: "first-time large repo contributor — ContribAI demo case"
description: "Demo case showing contribai-first-time-large-repo anti-pattern detection. 首次贡献者向大仓提 PR 没建立信用."
repo: kubernetes/kubernetes
pr_number: 999995
pr_url: https://github.com/kubernetes/kubernetes/pull/999995-demo
author: contribai-demo
final_status: closed-not-merged
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
links:
  - type: anti-pattern
    target: anti-patterns/contribai-first-time-large-repo.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +890 / -234 / 15 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 48.0
    maintainer_action: closed — first contribution, please discuss in issue first
    bot_review: []
    blocker: null
    resolution: trust_deficit
    close_reason: "This is a complex change from a first-time contributor. Please discuss the approach in an issue first and build trust with smaller contributions."
---

## Problem

First-time contributor submitted a complex PR to Kubernetes (123k stars) without establishing trust in the community.

## Root Cause

Contributor did not build trust before submitting a complex change. First-time contributors to large repos have low merge rates (< 5%).

## Detection

pr-genius `analyze_pr` flagged:
- `first_contributor_large_repo` signal (severity: medium)
- `needs_preflight` signal
- Checklist item: "build_trust" with hint to participate in issues first

## Fix Action

1. Build trust first: participate in issue discussions for 2-4 weeks
2. Start with simple fixes: typo corrections, documentation improvements
3. Then submit more complex changes
4. Always discuss approach in an issue first

## Prevention

For first-time contributions to large repos:
1. Participate in issue discussions first
2. Start with simple fixes
3. Build trust over time
4. Discuss complex changes in issues before submitting PRs
