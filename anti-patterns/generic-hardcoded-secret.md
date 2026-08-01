---type: Anti-Pattern
key: generic-hardcoded-secret
tags: [cron, scheduling, reliability]
description: "PR with hardcoded secret"
symptom: "Maintainer comments: 'Hardcoded secret'"
trigger_keywords:
  - "hardcoded secret"
  - "hardcoded password"
fix_action: "1) Remove secret; 2) Use environment variable"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-hardcoded-secret.md
updated: 2026-08-01
confidence: medium
---

# Hardcoded Secret

## Pattern

PRs with hardcoded secret get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Remove secret
2. Use environment variable
