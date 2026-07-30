---
type: Anti-Pattern
key: generic-data-retention
tags: [cron, scheduling, reliability]
description: "PR忽视数据保留"
symptom: "Maintainer comments: 'Data retention issue'"
trigger_keywords:
  - "data retention"
  - "data lifecycle"
fix_action: "1) Set retention; 2) Add cleanup"
created: 2026-07-29
severity: medium
---

# Data Retention

## Pattern

PRs忽视数据保留 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Set retention
2. Add cleanup
