---
type: Anti-Pattern
key: generic-no-chaos-engineering-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require chaos engineering"
symptom: "Maintainer comments: 'Please build chaos engineering'"
trigger_keywords:
  - "no chaos engineering"
  - "missing chaos engineering"
fix_action: "1) Build chaos engineering; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-chaos-engineering-large-repos.md
updated: 2026-08-01
confidence: medium
---

# No Chaos Engineering (Large Repos)

## Pattern

Large repos require chaos engineering for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build chaos engineering
2) Push fix
