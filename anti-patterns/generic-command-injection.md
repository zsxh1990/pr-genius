---
type: Anti-Pattern
key: generic-command-injection
description: "PR introducing command injection vulnerability"
symptom: "Maintainer comments: 'Command injection vulnerability'"
trigger_keywords:
  - "command injection"
  - "shell injection"
fix_action: "1) Use safe APIs; 2) Validate input"
severity: critical
---

# Command Injection

## Pattern

PRs introducing command injection vulnerability get rejected.

## How to Avoid

1. Use safe APIs
2. Validate input
