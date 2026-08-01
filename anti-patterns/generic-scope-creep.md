---type: Anti-Pattern
key: generic-scope-creep
tags: [cron, scheduling, reliability]
description: "PR with scope creep"
symptom: "Maintainer comments: 'Scope creep'"
trigger_keywords:
  - "scope creep"
  - "expanding scope"
fix_action: "1) Limit scope; 2) Separate PRs"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-scope-creep.md
updated: 2026-08-01
confidence: medium
---

# Scope Creep

## Pattern

PRs with scope creep get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Limit scope
2. Separate PRs
