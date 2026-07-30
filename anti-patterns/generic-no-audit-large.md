---
type: Anti-Pattern
key: generic-no-audit-large
tags: [cron, scheduling, reliability]
description: "Large repos require audit"
symptom: "Maintainer comments: 'Please build audit'"
trigger_keywords:
  - "no audit"
  - "missing audit"
fix_action: "1) Build audit; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Audit (Large Repos)

## Pattern

Large repos require audit for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build audit
2) Push fix
