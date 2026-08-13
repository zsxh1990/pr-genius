---
type: Anti-Pattern
key: generic-no-review-large
tags: [cron, scheduling, reliability]
description: "Large repos require review"
symptom: "Maintainer comments: 'Please request review'"
trigger_keywords:
  - "no review"
  - "missing review"
fix_action: "1) Request review; 2) Wait for approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-review-large.md
updated: 2026-08-01
confidence: medium

---

# No Review (Large Repos)

## Pattern

Large repos require review for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Request review
2. Wait for approval
