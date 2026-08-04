---
type: Anti-Pattern
key: generic-low-cohesion
tags: [cron, scheduling, reliability]
description: "PR with low cohesion"
symptom: "Maintainer comments: 'Low cohesion'"
trigger_keywords:
  - "low cohesion"
  - "unrelated functionality"
fix_action: "1) Increase cohesion; 2) Apply SRP"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-low-cohesion.md
updated: 2026-08-01
confidence: medium
---

# Low Cohesion

## Pattern

PRs with low cohesion get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Increase cohesion
2. Apply SRP
