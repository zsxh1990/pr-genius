---
type: Anti-Pattern
key: generic-circular-dependency
tags: [cron, scheduling, reliability]
description: "PR with circular dependency"
symptom: "Maintainer comments: 'Circular dependency'"
trigger_keywords:
  - "circular dependency"
  - "circular import"
fix_action: "1) Break cycle; 2) Restructure"
created: 2026-07-29
severity: high
---

# Circular Dependency

## Pattern

PRs with circular dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Break cycle
2. Restructure
