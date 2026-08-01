---type: Anti-Pattern
key: generic-no-postmortem-large
tags: [cron, scheduling, reliability]
description: "Large repos require postmortem"
symptom: "Maintainer comments: 'Please add postmortem'"
trigger_keywords:
  - "no postmortem"
  - "missing postmortem"
fix_action: "1) Add postmortem; 2) Push fix"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-postmortem-large.md
updated: 2026-08-01
confidence: medium
---

# No Postmortem (Large Repos)

## Pattern

Large repos require postmortem for all changes.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add postmortem
2. Push fix
