---
type: Anti-Pattern
key: generic-feature-creep
tags: [cron, scheduling, reliability]
description: "PR with feature creep"
symptom: "Maintainer comments: 'Feature creep'"
trigger_keywords:
  - "feature creep"
  - "too many features"
fix_action: "1) Limit features; 2) Separate PRs"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-feature-creep.md
updated: 2026-08-01
confidence: medium
---

# Feature Creep

## Pattern

PRs with feature creep get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Limit features
2. Separate PRs
