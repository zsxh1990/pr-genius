---
type: Anti-Pattern
key: generic-inappropriate-intimacy
tags: [cron, scheduling, reliability]
description: "PR with inappropriate intimacy"
symptom: "Maintainer comments: 'Inappropriate intimacy'"
trigger_keywords:
  - "inappropriate intimacy"
  - "knows too much"
fix_action: "1) Reduce coupling; 2) Use interfaces"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-inappropriate-intimacy.md
updated: 2026-08-01
confidence: medium
---

# Inappropriate Intimacy

## Pattern

PRs with inappropriate intimacy get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Reduce coupling
2. Use interfaces
