---type: Anti-Pattern
key: generic-large-pr
tags: [cron, scheduling, reliability]
description: "PR too large to review"
symptom: "Maintainer comments: 'PR too large'"
trigger_keywords:
  - "too large"
  - "too many changes"
fix_action: "1) Split PR; 2) Focus on one change"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-large-pr.md
updated: 2026-08-01
confidence: medium
---

# Large PR

## Pattern

PRs too large to review get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Split PR
2. Focus on one change
