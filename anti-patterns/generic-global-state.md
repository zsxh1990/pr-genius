---
type: Anti-Pattern
key: generic-global-state
tags: [cron, scheduling, reliability]
description: "PR with global state"
symptom: "Maintainer comments: 'Global state'"
trigger_keywords:
  - "global state"
  - "global variable"
fix_action: "1) Remove global state; 2) Use dependency injection"
created: 2026-07-29
severity: medium
---

# Global State

## Pattern

PRs with global state get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove global state
2. Use dependency injection
