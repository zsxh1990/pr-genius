---
type: Anti-Pattern
key: generic-ssrf
description: "PR introducing SSRF vulnerability"
symptom: "Maintainer comments: 'SSRF vulnerability'"
trigger_keywords:
  - "ssrf"
  - "server-side request forgery"
fix_action: "1) Validate URLs; 2) Whitelist domains"
created: 2026-07-29
severity: high
---

# SSRF

## Pattern

PRs introducing SSRF vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate URLs
2. Whitelist domains
