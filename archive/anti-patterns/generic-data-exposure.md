---
type: Anti-Pattern
key: generic-data-exposure
tags: [cron, scheduling, reliability]
description: "PR exposing sensitive data"
symptom: "Maintainer comments: 'Data exposure'"
trigger_keywords:
  - "data exposure"
  - "sensitive data"
fix_action: "1) Remove exposure; 2) Add encryption"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-data-exposure.md
updated: 2026-08-01
confidence: medium

---

# Data Exposure

## Pattern

PRs exposing sensitive data get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove exposure
2. Add encryption
