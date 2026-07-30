---
type: Anti-Pattern
key: generic-merge-conflict
tags: [cron, scheduling, reliability]
description: "PR with merge conflict"
symptom: "PR has conflicts"
trigger_keywords:
  - "merge conflict"
  - "conflicts"
fix_action: "1) Resolve conflicts; 2) Rebase on main"
created: 2026-07-29
severity: high
---

# Merge Conflict

## Pattern

PRs with merge conflict get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Resolve conflicts
2. Rebase on main
