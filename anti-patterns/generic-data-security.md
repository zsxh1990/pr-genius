---
type: Anti-Pattern
key: generic-data-security
tags: [cron, scheduling, reliability]
description: "PR忽视数据安全"
symptom: "Maintainer comments: 'Data security issue'"
trigger_keywords:
  - "data security"
  - "data encryption"
fix_action: "1) Encrypt data; 2) Add security"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-security.md
updated: 2026-08-01
confidence: medium
---

# Data Security

## Pattern

PRs忽视数据安全 get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Encrypt data
2. Add security
