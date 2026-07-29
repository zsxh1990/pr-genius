---
type: Anti-Pattern
key: generic-data-exposure
description: "PR exposing sensitive data"
symptom: "Maintainer comments: 'Data exposure'"
trigger_keywords:
  - "data exposure"
  - "sensitive data"
fix_action: "1) Remove exposure; 2) Add encryption"
severity: critical
---

# Data Exposure

## Pattern

PRs exposing sensitive data get rejected.

## How to Avoid

1. Remove exposure
2. Add encryption
