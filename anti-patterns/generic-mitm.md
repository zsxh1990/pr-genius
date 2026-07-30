---
type: Anti-Pattern
key: generic-mitm
description: "PR introducing MITM vulnerability"
symptom: "Maintainer comments: 'MITM vulnerability'"
trigger_keywords:
  - "mitm"
  - "man in the middle"
fix_action: "1) Use HTTPS; 2) Validate certificates"
created: 2026-07-29
severity: high
---

# MITM

## Pattern

PRs introducing MITM vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use HTTPS
2. Validate certificates
