---
type: Anti-Pattern
key: generic-no-security-large-repos
tags: [cron, scheduling, reliability]
description: "Large repos require security"
symptom: "Maintainer comments: 'Please build security'"
trigger_keywords:
  - "no security"
  - "missing security"
fix_action: "1) Build security; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Security (Large Repos)

## Pattern

Large repos require security for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build security
2) Push fix
