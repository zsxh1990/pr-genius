---
type: Anti-Pattern
key: generic-no-failure-tolerance-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require failure tolerance"
symptom: "Maintainer comments: 'Please build failure tolerance'"
trigger_keywords:
  - "no failure tolerance"
  - "missing failure tolerance"
fix_action: "1) Build failure tolerance; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-failure-tolerance-large-repos.md
updated: 2026-08-01
confidence: medium

---

# No Failure Tolerance (Large Repos)

## Pattern

Large repos require failure tolerance for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build failure tolerance
2) Push fix
