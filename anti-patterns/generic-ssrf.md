---type: Anti-Pattern
key: generic-ssrf
tags: [cron, scheduling, reliability]
description: "PR introducing SSRF vulnerability"
symptom: "Maintainer comments: 'SSRF vulnerability'"
trigger_keywords:
  - "ssrf"
  - "server-side request forgery"
fix_action: "1) Validate URLs; 2) Whitelist domains"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-ssrf.md
updated: 2026-08-01
confidence: medium
---

# SSRF

## Pattern

PRs introducing SSRF vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate URLs
2. Whitelist domains
