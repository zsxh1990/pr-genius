---type: Anti-Pattern
key: generic-command-injection
tags: [cron, scheduling, reliability]
description: "PR introducing command injection vulnerability"
symptom: "Maintainer comments: 'Command injection vulnerability'"
trigger_keywords:
  - "command injection"
  - "shell injection"
fix_action: "1) Use safe APIs; 2) Validate input"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-command-injection.md
updated: 2026-08-01
confidence: medium
---

# Command Injection

## Pattern

PRs introducing command injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use safe APIs
2. Validate input
