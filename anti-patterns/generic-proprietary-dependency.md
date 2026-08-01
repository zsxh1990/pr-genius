---type: Anti-Pattern
key: generic-proprietary-dependency
tags: [cron, scheduling, reliability]
description: "PR adding proprietary dependency"
symptom: "Maintainer comments: 'Proprietary dependency'"
trigger_keywords:
  - "proprietary dependency"
  - "closed source"
fix_action: "1) Use open source; 2) Abstract dependency"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-proprietary-dependency.md
updated: 2026-08-01
confidence: medium
---

# Proprietary Dependency

## Pattern

PRs adding proprietary dependency get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use open source
2. Abstract dependency
