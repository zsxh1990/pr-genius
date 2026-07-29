---
type: Anti-Pattern
key: generic-data-loss
description: "PR导致数据丢失"
symptom: "Maintainer comments: 'Data loss'"
trigger_keywords:
  - "data loss"
  - "data deletion"
fix_action: "1) Add backups; 2) Add soft delete"
severity: critical
---

# Data Loss

## Pattern

PRs导致数据丢失 get rejected.

## How to Avoid

1. Add backups
2. Add soft delete
