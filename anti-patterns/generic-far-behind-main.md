---
type: Anti-Pattern
key: generic-far-behind-main
tags: [cron, scheduling, reliability]
description: "PR far behind main"
symptom: "Maintainer comments: 'X commits behind main'"
trigger_keywords:
  - "commits behind"
  - "far behind"
fix_action: "1) Rebase on main; 2) Resolve conflicts"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-far-behind-main.md
updated: 2026-08-01
confidence: medium
---

# Far Behind Main

## Pattern

PRs far behind main get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Rebase on main regularly
2. Resolve conflicts
