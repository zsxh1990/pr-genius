---type: Anti-Pattern
key: generic-no-issue
tags: [cron, scheduling, reliability]
description: "PR without linked issue"
symptom: "Maintainer comments: 'Please link issue'"
trigger_keywords:
  - "no issue"
  - "missing issue"
fix_action: "1) Create issue; 2) Link PR"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-issue.md
updated: 2026-08-01
confidence: medium
---

# No Issue

## Pattern

PRs without linked issue get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Create issue
2. Link PR
