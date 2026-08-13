---
type: Anti-Pattern
key: generic-no-logging-large
tags: [cron, scheduling, reliability]
description: "Large repos require logging"
symptom: "Maintainer comments: 'Please add logging'"
trigger_keywords:
  - "no logging"
  - "missing logging"
fix_action: "1) Add logging; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-logging-large.md
updated: 2026-08-01
confidence: medium

---

# No Logging (Large Repos)

## Pattern

Large repos require logging for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add logging
2. Push fix
