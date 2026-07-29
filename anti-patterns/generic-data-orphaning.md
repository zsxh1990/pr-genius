---
type: Anti-Pattern
key: generic-data-orphaning
description: "PR导致数据孤立"
symptom: "Maintainer comments: 'Data orphaning'"
trigger_keywords:
  - "data orphaning"
  - "orphan records"
fix_action: "1) Add foreign keys; 2) Add cascading"
severity: medium
---

# Data Orphaning

## Pattern

PRs导致数据孤立 get rejected.

## How to Avoid

1. Add foreign keys
2. Add cascading
