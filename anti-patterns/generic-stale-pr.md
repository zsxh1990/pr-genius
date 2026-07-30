---
type: Anti-Pattern
key: generic-stale-pr
description: "PR marked as stale"
symptom: "PR labeled as 'stale'"
trigger_keywords:
  - "stale"
  - "waiting on author"
fix_action: "1) Rebase on main; 2) Respond to comments"
created: 2026-07-29
severity: medium
---

# Stale PR

## Pattern

PRs marked as stale get closed after timeout.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Rebase on main regularly
2. Respond to comments promptly
