---
type: Anti-Pattern
key: generic-mitm
tags: [cron, scheduling, reliability]
description: "PR introducing MITM vulnerability"
symptom: "Maintainer comments: 'MITM vulnerability'"
trigger_keywords:
  - "mitm"
  - "man in the middle"
fix_action: "1) Use HTTPS; 2) Validate certificates"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-mitm.md
updated: 2026-08-01
confidence: medium
---

# MITM

## Pattern

PRs introducing MITM vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use HTTPS
2. Validate certificates
