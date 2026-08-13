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
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-audit-large.md
updated: 2026-08-01
confidence: medium

---

# No Audit (Large Repos)

## Pattern

Large repos require audit for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build audit
2) Push fix
