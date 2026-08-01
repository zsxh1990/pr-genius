---type: Anti-Pattern
key: generic-xxe
tags: [cron, scheduling, reliability]
description: "PR introducing XXE vulnerability"
symptom: "Maintainer comments: 'XXE vulnerability'"
trigger_keywords:
  - "xxe"
  - "xml external entity"
fix_action: "1) Disable external entities; 2) Validate XML"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-xxe.md
updated: 2026-08-01
confidence: medium
---

# XXE

## Pattern

PRs introducing XXE vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Disable external entities
2. Validate XML
