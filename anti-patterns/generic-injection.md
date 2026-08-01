---type: Anti-Pattern
key: generic-injection
tags: [cron, scheduling, reliability]
description: "PR introducing injection vulnerability"
symptom: "Maintainer comments: 'Injection vulnerability'"
trigger_keywords:
  - "injection"
  - "sql injection"
  - "xss"
fix_action: "1) Sanitize input; 2) Use parameterized queries"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-injection.md
updated: 2026-08-01
confidence: medium
---

# Injection

## Pattern

PRs introducing injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Sanitize input
2. Use parameterized queries
