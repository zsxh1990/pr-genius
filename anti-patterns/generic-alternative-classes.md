---
type: Anti-Pattern
key: generic-alternative-classes
tags: [cron, scheduling, reliability]
description: "PR with alternative classes"
symptom: "Maintainer comments: 'Alternative classes'"
trigger_keywords:
  - "alternative classes"
  - "duplicate interfaces"
fix_action: "1) Unify classes; 2) Use common interface"
created: 2026-07-29
severity: low
---

# Alternative Classes

## Pattern

PRs with alternative classes get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Unify classes
2. Use common interface
