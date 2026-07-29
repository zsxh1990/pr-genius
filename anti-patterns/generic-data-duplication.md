---
type: Anti-Pattern
key: generic-data-duplication
description: "PR导致数据重复"
symptom: "Maintainer comments: 'Data duplication'"
trigger_keywords:
  - "data duplication"
  - "duplicate records"
fix_action: "1) Add deduplication; 2) Add unique constraints"
severity: medium
---

# Data Duplication

## Pattern

PRs导致数据重复 get rejected.

## How to Avoid

1. Add deduplication
2. Add unique constraints
