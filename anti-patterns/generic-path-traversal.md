---type: Anti-Pattern
key: generic-path-traversal
tags: [cron, scheduling, reliability]
description: "PR introducing path traversal vulnerability"
symptom: "Maintainer comments: 'Path traversal vulnerability'"
trigger_keywords:
  - "path traversal"
  - "directory traversal"
fix_action: "1) Validate paths; 2) Use chroot"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-path-traversal.md
updated: 2026-08-01
confidence: medium
---

# Path Traversal

## Pattern

PRs introducing path traversal vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate paths
2. Use chroot
