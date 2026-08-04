---
type: Anti-Pattern
key: generic-deprecated-api
tags: [cron, scheduling, reliability]
description: "PR using deprecated API"
symptom: "Maintainer comments: 'Deprecated API'"
trigger_keywords:
  - "deprecated api"
  - "deprecated function"
fix_action: "1) Use new API; 2) Update code"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-deprecated-api.md
updated: 2026-08-01
confidence: medium
---

# Deprecated API

## Pattern

PRs using deprecated API get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Use new API
2. Update code
