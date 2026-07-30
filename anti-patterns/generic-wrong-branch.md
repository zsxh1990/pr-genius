---
type: Anti-Pattern
key: generic-wrong-branch
tags: [cron, scheduling, reliability]
description: "PR targeting wrong branch"
symptom: "Maintainer comments: 'Please target correct branch'"
trigger_keywords:
  - "wrong branch"
  - "incorrect branch"
fix_action: "1) Retarget branch; 2) Rebase"
created: 2026-07-29
severity: medium
---

# Wrong Branch

## Pattern

PRs targeting wrong branch get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Retarget branch
2. Rebase
