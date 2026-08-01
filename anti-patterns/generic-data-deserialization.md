---type: Anti-Pattern
key: generic-data-deserialization
tags: [cron, scheduling, reliability]
description: "PR忽视数据反序列化"
symptom: "Maintainer comments: 'Data deserialization issue'"
trigger_keywords:
  - "data deserialization"
  - "json deserialization"
fix_action: "1) Fix deserialization; 2) Add tests"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-deserialization.md
updated: 2026-08-01
confidence: medium
---

# Data Deserialization

## Pattern

PRs忽视数据反序列化 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix deserialization
2. Add tests
