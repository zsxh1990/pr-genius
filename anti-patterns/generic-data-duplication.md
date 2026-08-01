---type: Anti-Pattern
key: generic-data-duplication
tags: [cron, scheduling, reliability]
description: "PR导致数据重复"
symptom: "Maintainer comments: 'Data duplication'"
trigger_keywords:
  - "data duplication"
  - "duplicate records"
fix_action: "1) Add deduplication; 2) Add unique constraints"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-duplication.md
updated: 2026-08-01
confidence: medium
---

# Data Duplication

## Pattern

PRs导致数据重复 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add deduplication
2. Add unique constraints
