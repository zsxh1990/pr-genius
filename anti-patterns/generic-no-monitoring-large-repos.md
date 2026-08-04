---
type: Anti-Pattern
key: generic-no-monitoring-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require monitoring"
symptom: "Maintainer comments: 'Please build monitoring'"
trigger_keywords:
  - "no monitoring"
  - "missing monitoring"
fix_action: "1) Build monitoring; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-monitoring-large-repos.md
updated: 2026-08-01
confidence: medium
---

# No Monitoring (Large Repos)

## Pattern

Large repos require monitoring for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build monitoring
2) Push fix
