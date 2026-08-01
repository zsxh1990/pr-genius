---type: Anti-Pattern
key: generic-refused-bequest
tags: [cron, scheduling, reliability]
description: "PR with refused bequest"
symptom: "Maintainer comments: 'Refused bequest'"
trigger_keywords:
  - "refused bequest"
  - "broken inheritance"
fix_action: "1) Fix inheritance; 2) Use composition"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-refused-bequest.md
updated: 2026-08-01
confidence: medium
---

# Refused Bequest

## Pattern

PRs with refused bequest get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix inheritance
2. Use composition
