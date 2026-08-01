---type: Anti-Pattern
key: generic-schema-change
tags: [cron, scheduling, reliability]
description: "PR with schema change"
symptom: "Maintainer comments: 'Schema change'"
trigger_keywords:
  - "schema change"
  - "database change"
fix_action: "1) Add migration; 2) Get approval"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-schema-change.md
updated: 2026-08-01
confidence: medium
---

# Schema Change

## Pattern

PRs with schema change get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add migration
2. Get approval
