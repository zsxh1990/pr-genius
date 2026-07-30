---
type: Anti-Pattern
key: generic-command-injection
description: "PR introducing command injection vulnerability"
symptom: "Maintainer comments: 'Command injection vulnerability'"
trigger_keywords:
  - "command injection"
  - "shell injection"
fix_action: "1) Use safe APIs; 2) Validate input"
created: 2026-07-29
severity: critical
---

# Command Injection

## Pattern

PRs introducing command injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use safe APIs
2. Validate input
