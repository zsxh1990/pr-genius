---type: Anti-Pattern
key: generic-data-lineage
tags: [cron, scheduling, reliability]
description: "PR忽视数据血缘"
symptom: "Maintainer comments: 'Data lineage issue'"
trigger_keywords:
  - "data lineage"
  - "data provenance"
fix_action: "1) Track lineage; 2) Document sources"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-lineage.md
updated: 2026-08-01
confidence: medium
---

# Data Lineage

## Pattern

PRs忽视数据血缘 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Track lineage
2. Document sources
