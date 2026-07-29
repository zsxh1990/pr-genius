---
type: Anti-Pattern
key: generic-data-deserialization
description: "PR忽视数据反序列化"
symptom: "Maintainer comments: 'Data deserialization issue'"
trigger_keywords:
  - "data deserialization"
  - "json deserialization"
fix_action: "1) Fix deserialization; 2) Add tests"
severity: medium
---

# Data Deserialization

## Pattern

PRs忽视数据反序列化 get rejected.

## How to Avoid

1. Fix deserialization
2. Add tests
