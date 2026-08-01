---type: Anti-Pattern
key: generic-resource-leak
tags: [cron, scheduling, reliability]
description: "PR introducing resource leak"
symptom: "Maintainer comments: 'Resource leak'"
trigger_keywords:
  - "resource leak"
  - "file handle leak"
fix_action: "1) Close resources; 2) Use try-with-resources"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-resource-leak.md
updated: 2026-08-01
confidence: medium
---

# Resource Leak

## Pattern

PRs introducing resource leak get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Close resources
2. Use try-with-resources
