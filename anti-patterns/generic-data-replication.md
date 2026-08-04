---
type: Anti-Pattern
key: generic-data-replication
tags: [cron, scheduling, reliability]
description: "PR忽视数据复制"
symptom: "Maintainer comments: 'Data replication issue'"
trigger_keywords:
  - "data replication"
  - "master slave"
fix_action: "1) Add replication; 2) Handle consistency"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-replication.md
updated: 2026-08-01
confidence: medium
---

# Data Replication

## Pattern

PRs忽视数据复制 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add replication
2. Handle consistency
