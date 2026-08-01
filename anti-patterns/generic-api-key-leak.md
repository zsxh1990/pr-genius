---type: Anti-Pattern
key: generic-api-key-leak
tags: [cron, scheduling, reliability]
description: "PR introducing API key leak vulnerability"
symptom: "Maintainer comments: 'API key leak vulnerability'"
trigger_keywords:
  - "api key leak"
  - "secret leak"
fix_action: "1) Rotate keys; 2) Use secure storage"
created: 2026-07-29
severity: critical
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-api-key-leak.md
updated: 2026-08-01
confidence: medium
---

# API Key Leak

## Pattern

PRs introducing API key leak vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Rotate keys
2. Use secure storage
