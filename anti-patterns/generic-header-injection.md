---
type: Anti-Pattern
key: generic-header-injection
description: "PR introducing header injection vulnerability"
symptom: "Maintainer comments: 'Header injection vulnerability'"
trigger_keywords:
  - "header injection"
  - "http header injection"
fix_action: "1) Validate headers; 2) Sanitize output"
created: 2026-07-29
severity: high
---

# Header Injection

## Pattern

PRs introducing header injection vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate headers
2. Sanitize output
