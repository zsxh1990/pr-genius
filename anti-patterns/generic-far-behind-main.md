---
type: Anti-Pattern
key: generic-far-behind-main
description: "PR far behind main"
symptom: "Maintainer comments: 'X commits behind main'"
trigger_keywords:
  - "commits behind"
  - "far behind"
fix_action: "1) Rebase on main; 2) Resolve conflicts"
severity: high
---

# Far Behind Main

## Pattern

PRs far behind main get rejected.

## How to Avoid

1. Rebase on main regularly
2. Resolve conflicts
