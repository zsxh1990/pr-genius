---
type: Anti-Pattern
key: generic-data-enrichment
tags: [cron, scheduling, reliability]
description: "PR忽视数据丰富"
symptom: "Maintainer comments: 'Data enrichment issue'"
trigger_keywords:
  - "data enrichment"
  - "data augmentation"
fix_action: "1) Add enrichment; 2) Add tests"
created: 2026-07-29
severity: medium
---

# Data Enrichment

## Pattern

PRs忽视数据丰富 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add enrichment
2. Add tests
