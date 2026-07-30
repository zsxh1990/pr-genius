---
type: Anti-Pattern
key: generic-deep-nesting
tags: [cron, scheduling, reliability]
description: "PR with deep nesting"
symptom: "Maintainer comments: 'Deep nesting'"
trigger_keywords:
  - "deep nesting"
  - "arrow code"
fix_action: "1) Flatten nesting; 2) Use early returns"
created: 2026-07-29
severity: low
---

# Deep Nesting

## Pattern

PRs with deep nesting get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Flatten nesting
2. Use early returns
