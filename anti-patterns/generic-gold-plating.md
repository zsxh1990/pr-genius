---
type: Anti-Pattern
key: generic-gold-plating
tags: [cron, scheduling, reliability]
description: "PR with gold plating"
symptom: "Maintainer comments: 'Gold plating'"
trigger_keywords:
  - "gold plating"
  - "unnecessary features"
fix_action: "1) Remove extras; 2) Focus on requirements"
created: 2026-07-29
severity: low
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-gold-plating.md
updated: 2026-08-01
confidence: medium
---

# Gold Plating

## Pattern

PRs with gold plating get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove extras
2. Focus on requirements
