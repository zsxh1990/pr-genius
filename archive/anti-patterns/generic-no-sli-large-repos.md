---
type: Anti-Pattern
key: generic-no-sli-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require SLI"
symptom: "Maintainer comments: 'Please build SLI'"
trigger_keywords:
  - "no sli"
  - "missing sli"
fix_action: "1) Build SLI; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-sli-large-repos.md
updated: 2026-08-01
confidence: medium

---

# No SLI (Large Repos)

## Pattern

Large repos require SLI for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build SLI
2) Push fix
