---
type: Anti-Pattern
key: generic-data-corruption
description: "PR导致数据损坏"
symptom: "Maintainer comments: 'Data corruption'"
trigger_keywords:
  - "data corruption"
  - "data loss"
fix_action: "1) Add checksums; 2) Add validation"
severity: critical
---

# Data Corruption

## Pattern

PRs导致数据损坏 get rejected.

## How to Avoid

1. Add checksums
2. Add validation
