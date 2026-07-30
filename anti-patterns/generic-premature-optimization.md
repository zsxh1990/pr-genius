---
type: Anti-Pattern
key: generic-premature-optimization
tags: [cron, scheduling, reliability]
description: "PR with premature optimization"
symptom: "Maintainer comments: 'Premature optimization'"
trigger_keywords:
  - "premature optimization"
  - "optimize early"
fix_action: "1) Profile first; 2) Optimize when needed"
created: 2026-07-29
severity: medium
---

# Premature Optimization

## Pattern

PRs with premature optimization get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Profile first
2. Optimize when needed
