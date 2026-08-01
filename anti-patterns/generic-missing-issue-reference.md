---type: Anti-Pattern
key: generic-missing-issue-reference
tags: [cron, scheduling, reliability]
description: "PR without linked issue"
symptom: "Maintainer comments: 'Please link to an issue'"
trigger_keywords:
  - "missing issue"
  - "no issue"
fix_action: "1) Create issue first; 2) Link PR to issue"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-missing-issue-reference.md
updated: 2026-08-01
confidence: medium
---

# Missing Issue Reference

## Pattern

PRs without linked issues get rejected in repos that require issue-first workflow.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Create issue first
2. Link PR to issue
