---
type: Anti-Pattern
key: generic-data-replication
description: "PR忽视数据复制"
symptom: "Maintainer comments: 'Data replication issue'"
trigger_keywords:
  - "data replication"
  - "master slave"
fix_action: "1) Add replication; 2) Handle consistency"
severity: high
---

# Data Replication

## Pattern

PRs忽视数据复制 get rejected.

## How to Avoid

1. Add replication
2. Handle consistency
