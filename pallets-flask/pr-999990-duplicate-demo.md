---
type: PR Case Study
title: "duplicate PR detection — ContribAI demo case"
description: "Demo case showing contribai-duplicate-pr anti-pattern detection. 提交前未搜索已有 PR/Issue, 导致重复提交."
repo: pallets/flask
pr_number: 999990
pr_url: https://github.com/pallets/flask/pull/999990-demo
author: contribai-demo
final_status: closed-not-merged
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
links:
  - type: anti-pattern
    target: anti-patterns/contribai-duplicate-pr.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +45 / -3 / 2 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 0.5
    maintainer_action: closed as duplicate of #4521
    bot_review: []
    blocker: null
    resolution: duplicate
    close_reason: "Already fixed in #4521, please search existing PRs before submitting"
---

## Problem

Contributor submitted a PR to fix session cookie handling on redirect, but the same fix was already merged in PR #4521 two weeks earlier.

## Root Cause

Contributor did not search existing PRs before submitting. `gh search prs --repo pallets/flask --state all "session cookie redirect"` would have found #4521 immediately.

## Detection

pr-genius `analyze_pr` flagged:
- `needs_preflight` signal (no policy for repo)
- Checklist item: "check_duplicate" with hint to search existing PRs

## Fix Action

1. Search existing PRs: `gh search prs --repo org/repo --state all "<keyword>"`
2. Search existing issues: `gh search issues --repo org/repo --state all "<keyword>"`
3. Check main branch: `git fetch origin main && git log origin/main | head -20`
4. If duplicate found, close own PR and reference existing one

## Prevention

Always search before submitting:
```bash
gh search prs --repo org/repo --state all "session cookie redirect"
gh search issues --repo org/repo --state all "session cookie"
git fetch origin main && git log origin/main --oneline | head -20
```
