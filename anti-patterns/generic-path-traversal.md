---
type: Anti-Pattern
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
---

# Path Traversal

## Pattern

PRs introducing path traversal vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Validate paths
2. Use chroot
