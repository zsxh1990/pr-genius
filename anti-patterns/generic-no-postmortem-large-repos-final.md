---
type: Anti-Pattern
key: generic-no-postmortem-large-repos-final
tags: [cron, scheduling, reliability]
description: "Large repos require postmortem"
symptom: "Maintainer comments: 'Please build postmortem'"
trigger_keywords:
  - "no postmortem"
  - "missing postmortem"
fix_action: "1) Build postmortem; 2) Push fix"
created: 2026-07-29
severity: high
---

# No Postmortem (Large Repos)

## Pattern

Large repos require postmortem for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1) Build postmortem
2) Push fix
