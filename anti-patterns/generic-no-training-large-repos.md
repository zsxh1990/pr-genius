---
type: Anti-Pattern
key: generic-no-training-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require training"
symptom: "Maintainer comments: 'Please build training'"
trigger_keywords:
  - "no training"
  - "missing training"
fix_action: "1) Build training; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Training (Large Repos)

## Pattern

Large repos require training for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build training
2) Push fix
