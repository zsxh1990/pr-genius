---
type: Anti-Pattern
key: generic-data-exposure
description: "PR exposing sensitive data"
symptom: "Maintainer comments: 'Data exposure'"
trigger_keywords:
  - "data exposure"
  - "sensitive data"
fix_action: "1) Remove exposure; 2) Add encryption"
created: 2026-07-29
severity: critical
---

# Data Exposure

## Pattern

PRs exposing sensitive data get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove exposure
2. Add encryption
