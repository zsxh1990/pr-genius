---
type: Anti-Pattern
key: generic-ssrf
description: "PR introducing SSRF vulnerability"
symptom: "Maintainer comments: 'SSRF vulnerability'"
trigger_keywords:
  - "ssrf"
  - "server-side request forgery"
fix_action: "1) Validate URLs; 2) Whitelist domains"
severity: high
---

# SSRF

## Pattern

PRs introducing SSRF vulnerability get rejected.

## How to Avoid

1. Validate URLs
2. Whitelist domains
