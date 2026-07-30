---
type: Anti-Pattern
key: generic-no-alerting-large
tags: [cron, scheduling, reliability]
description: "Large repos require alerting"
symptom: "Maintainer comments: 'Please add alerting'"
trigger_keywords:
  - "no alerting"
  - "missing alerting"
fix_action: "1) Add alerting; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Alerting (Large Repos)

## Pattern

Large repos require alerting for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add alerting
2. Push fix
