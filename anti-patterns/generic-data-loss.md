---
type: Anti-Pattern
key: generic-data-loss
tags: [cron, scheduling, reliability]
description: "PR导致数据丢失"
symptom: "Maintainer comments: 'Data loss'"
trigger_keywords:
  - "data loss"
  - "data deletion"
fix_action: "1) Add backups; 2) Add soft delete"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-loss.md
updated: 2026-08-01
confidence: medium
---

# Data Loss

## Pattern

PRs导致数据丢失 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add backups
2. Add soft delete
