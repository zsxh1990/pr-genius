---
type: Anti-Pattern
key: generic-data-catalog
tags: [cron, scheduling, reliability]
description: "PR忽视数据目录"
symptom: "Maintainer comments: 'Data catalog issue'"
trigger_keywords:
  - "data catalog"
  - "metadata"
fix_action: "1) Maintain catalog; 2) Document metadata"
created: 2026-07-29
severity: medium
---

# Data Catalog

## Pattern

PRs忽视数据目录 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Maintain catalog
2. Document metadata
