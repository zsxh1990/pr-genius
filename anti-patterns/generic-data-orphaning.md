---
type: Anti-Pattern
key: generic-data-orphaning
tags: [cron, scheduling, reliability]
description: "PR导致数据孤立"
symptom: "Maintainer comments: 'Data orphaning'"
trigger_keywords:
  - "data orphaning"
  - "orphan records"
fix_action: "1) Add foreign keys; 2) Add cascading"
created: 2026-07-29
severity: medium
---

# Data Orphaning

## Pattern

PRs导致数据孤立 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add foreign keys
2. Add cascading
