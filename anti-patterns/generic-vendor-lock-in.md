---type: Anti-Pattern
key: generic-vendor-lock-in
tags: [cron, scheduling, reliability]
description: "PR introducing vendor lock-in"
symptom: "Maintainer comments: 'Vendor lock-in'"
trigger_keywords:
  - "vendor lock-in"
  - "proprietary dependency"
fix_action: "1) Use open standards; 2) Abstract vendor"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-vendor-lock-in.md
updated: 2026-08-01
confidence: medium
---

# Vendor Lock-in

## Pattern

PRs introducing vendor lock-in get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use open standards
2. Abstract vendor
