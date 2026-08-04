---
type: Anti-Pattern
key: generic-no-approval
tags: [cron, scheduling, reliability]
description: "PR without approval"
symptom: "Maintainer comments: 'Please get approval'"
trigger_keywords:
  - "no approval"
  - "missing approval"
fix_action: "1) Get approval; 2) Wait for merge"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-approval.md
updated: 2026-08-01
confidence: medium
---

# No Approval

## Pattern

PRs without approval get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Get approval
2. Wait for merge
