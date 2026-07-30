---
type: Anti-Pattern
key: generic-data-encoding
description: "PR忽视数据编码"
symptom: "Maintainer comments: 'Data encoding issue'"
trigger_keywords:
  - "data encoding"
  - "character encoding"
fix_action: "1) Fix encoding; 2) Add validation"
created: 2026-07-29
severity: medium
---

# Data Encoding

## Pattern

PRs忽视数据编码 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Fix encoding
2. Add validation
