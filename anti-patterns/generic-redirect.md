---type: Anti-Pattern
key: generic-redirect
tags: [cron, scheduling, reliability]
description: "PR introducing open redirect vulnerability"
symptom: "Maintainer comments: 'Open redirect vulnerability'"
trigger_keywords:
  - "open redirect"
  - "redirect vulnerability"
fix_action: "1) Validate URLs; 2) Whitelist domains"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-redirect.md
updated: 2026-08-01
confidence: medium
---

# Open Redirect

## Pattern

PRs introducing open redirect vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate URLs
2. Whitelist domains
