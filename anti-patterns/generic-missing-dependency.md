---type: Anti-Pattern
key: generic-missing-dependency
tags: [cron, scheduling, reliability]
description: "PR with missing dependency"
symptom: "Maintainer comments: 'Missing dependency'"
trigger_keywords:
  - "missing dependency"
  - "not found"
fix_action: "1) Add dependency; 2) Update requirements"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-missing-dependency.md
updated: 2026-08-01
confidence: medium
---

# Missing Dependency

## Pattern

PRs with missing dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add dependency
2. Update requirements
