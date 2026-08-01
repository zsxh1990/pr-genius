---type: Anti-Pattern
key: generic-wrong-repo
tags: [cron, scheduling, reliability]
description: "PR to wrong repo"
symptom: "Maintainer comments: 'Wrong repo'"
trigger_keywords:
  - "wrong repo"
  - "incorrect repo"
fix_action: "1) Close PR; 2) Submit to correct repo"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-wrong-repo.md
updated: 2026-08-01
confidence: medium
---

# Wrong Repo

## Pattern

PRs to wrong repo get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Close PR
2. Submit to correct repo
