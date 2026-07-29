---
type: Anti-Pattern
key: generic-stale-pr
description: "PR marked as stale"
symptom: "PR labeled as 'stale'"
trigger_keywords:
  - "stale"
  - "waiting on author"
fix_action: "1) Rebase on main; 2) Respond to comments"
severity: medium
---

# Stale PR

## Pattern

PRs marked as stale get closed after timeout.

## How to Avoid

1. Rebase on main regularly
2. Respond to comments promptly
