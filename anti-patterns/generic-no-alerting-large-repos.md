---type: Anti-Pattern
key: generic-no-alerting-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require alerting"
symptom: "Maintainer comments: 'Please build alerting'"
trigger_keywords:
  - "no alerting"
  - "missing alerting"
fix_action: "1) Build alerting; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-alerting-large-repos.md
updated: 2026-08-01
confidence: medium
---

# No Alerting (Large Repos)

## Pattern

Large repos require alerting for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build alerting
2) Push fix
