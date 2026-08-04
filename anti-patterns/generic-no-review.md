---
type: Anti-Pattern
key: generic-no-review
tags: [cron, scheduling, reliability]
description: "PR without review"
symptom: "Maintainer comments: 'Please request review'"
trigger_keywords:
  - "no review"
  - "missing review"
fix_action: "1) Request review; 2) Wait for approval"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-review.md
updated: 2026-08-01
confidence: medium
---

# No Review

## Pattern

PRs without review get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Request review
2. Wait for approval
