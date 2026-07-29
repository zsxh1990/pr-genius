---
type: Anti-Pattern
key: generic-mitm
description: "PR introducing MITM vulnerability"
symptom: "Maintainer comments: 'MITM vulnerability'"
trigger_keywords:
  - "mitm"
  - "man in the middle"
fix_action: "1) Use HTTPS; 2) Validate certificates"
severity: high
---

# MITM

## Pattern

PRs introducing MITM vulnerability get rejected.

## How to Avoid

1. Use HTTPS
2. Validate certificates
