---type: Anti-Pattern
key: generic-version-conflict
tags: [cron, scheduling, reliability]
description: "PR with version conflict"
symptom: "Maintainer comments: 'Version conflict'"
trigger_keywords:
  - "version conflict"
  - "dependency conflict"
fix_action: "1) Resolve conflict; 2) Update versions"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-version-conflict.md
updated: 2026-08-01
confidence: medium
---

# Version Conflict

## Pattern

PRs with version conflict get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Resolve conflict
2. Update versions
