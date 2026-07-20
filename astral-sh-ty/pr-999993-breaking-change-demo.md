---
type: PR Case Study
title: "breaking change detection — ContribAI demo case"
description: "Demo case showing contribai-breaking-change-no-migration anti-pattern detection. 提交了 breaking change 但没提供 migration path."
repo: astral-sh/ty
pr_number: 999993
pr_url: https://github.com/astral-sh/ty/pull/999993-demo
author: contribai-demo
final_status: closed-not-merged
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
links:
  - type: anti-pattern
    target: anti-patterns/contribai-breaking-change-no-migration.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +312 / -156 / 8 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 2.0
    maintainer_action: closed — breaking change without migration
    bot_review: []
    blocker: null
    resolution: breaking_change
    close_reason: "This PR introduces breaking changes to the public API without a migration path. Please open an RFC first to discuss the deprecation strategy."
---

## Problem

Contributor submitted a PR that changed the public API signature without providing migration path, feature flag, or deprecation cycle.

## Root Cause

Contributor did not check if the change was breaking, and did not provide migration documentation or feature flags.

## Detection

pr-genius `analyze_pr` flagged:
- `needs_preflight` signal
- Checklist item: "check_breaking_change" with hint to check API changes

## Fix Action

1. Check if change is breaking: compare API signatures
2. If breaking, provide migration path (codemod, docs)
3. Use feature flag to default off
4. Add deprecation warning
5. Open RFC first to discuss deprecation cycle

## Prevention

Always check for breaking changes:
```bash
grep -r "deprecated\|removed\|changed" --include="*.py" | head -10
```
