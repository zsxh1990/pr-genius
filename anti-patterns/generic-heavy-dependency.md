---type: Anti-Pattern
key: generic-heavy-dependency
tags: [cron, scheduling, reliability]
description: "PR adding heavy dependency"
symptom: "Maintainer comments: 'Heavy dependency'"
trigger_keywords:
  - "heavy dependency"
  - "large dependency"
fix_action: "1) Use lighter alternative; 2) Implement locally"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-heavy-dependency.md
updated: 2026-08-01
confidence: medium
---

# Heavy Dependency

## Pattern

PRs adding heavy dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use lighter alternative
2. Implement locally
