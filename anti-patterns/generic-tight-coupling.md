---
type: Anti-Pattern
key: generic-tight-coupling
tags: [cron, scheduling, reliability]
description: "PR with tight coupling"
symptom: "Maintainer comments: 'Tight coupling'"
trigger_keywords:
  - "tight coupling"
  - "high coupling"
fix_action: "1) Use interfaces; 2) Apply DIP"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-tight-coupling.md
updated: 2026-08-01
confidence: medium
---

# Tight Coupling

## Pattern

PRs with tight coupling get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use interfaces
2. Apply DIP
