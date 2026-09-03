---
type: Anti-Pattern
key: generic-force-push
tags: [cron, scheduling, reliability]
description: "Force push to shared branch"
symptom: "Maintainer comments: 'Please don't force push'"
trigger_keywords:
  - "force push"
  - "force-with-lease"
fix_action: "1) Use merge commit; 2) Rebase locally"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-force-push.md
updated: 2026-08-01
confidence: medium

---

# Force Push

## Pattern

Force push to shared branch gets rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use merge commit
2. Rebase locally
