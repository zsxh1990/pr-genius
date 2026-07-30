---
type: Anti-Pattern
key: generic-data-serialization
tags: [cron, scheduling, reliability]
description: "PR忽视数据序列化"
symptom: "Maintainer comments: 'Data serialization issue'"
trigger_keywords:
  - "data serialization"
  - "json serialization"
fix_action: "1) Fix serialization; 2) Add tests"
created: 2026-07-29
severity: medium
---

# Data Serialization

## Pattern

PRs忽视数据序列化 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix serialization
2. Add tests
