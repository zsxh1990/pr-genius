---
type: Anti-Pattern
key: generic-singleton
tags: [cron, scheduling, reliability]
description: "PR with singleton pattern"
symptom: "Maintainer comments: 'Singleton pattern'"
trigger_keywords:
  - "singleton"
  - "global instance"
fix_action: "1) Use dependency injection; 2) Remove singleton"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-singleton.md
updated: 2026-08-01
confidence: medium
---

# Singleton Pattern

## Pattern

PRs with singleton pattern get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use dependency injection
2. Remove singleton
