---
type: PR Case Study
title: "archived repo detection — ContribAI demo case"
description: "Demo case showing contribai-archived-repo anti-pattern detection. 提 PR 前没查 repo 状态."
repo: pandas-dev/pandas
pr_number: 999991
pr_url: https://github.com/pandas-dev/pandas/pull/999991-demo
author: contribai-demo
final_status: closed-not-merged
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
links:
  - type: anti-pattern
    target: anti-patterns/contribai-archived-repo.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +120 / -45 / 3 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 0.5
    maintainer_action: closed — repo archived
    bot_review: []
    blocker: null
    resolution: archived
    close_reason: "This repository is archived and no longer accepts contributions. Please see pandas-dev/pandas-stubs for the successor project."
---

## Problem

Contributor submitted a PR to an archived repository that no longer accepts contributions.

## Root Cause

Contributor did not check repository status before submitting. `gh repo view org/repo --json isArchived` would have detected the archived state.

## Detection

pr-genius `analyze_pr` flagged:
- `needs_preflight` signal
- Checklist item: "check_repo_status" with hint to check archived state

## Fix Action

1. Check repo status: `gh repo view org/repo --json isArchived,isDisabled`
2. If archived, search for successor project
3. Redirect contribution to successor project

## Prevention

Always check repo status before submitting:
```bash
gh repo view org/repo --json isArchived,isDisabled
```
