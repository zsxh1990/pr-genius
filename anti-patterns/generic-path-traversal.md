---
type: Anti-Pattern
key: generic-path-traversal
description: "PR introducing path traversal vulnerability"
symptom: "Maintainer comments: 'Path traversal vulnerability'"
trigger_keywords:
  - "path traversal"
  - "directory traversal"
fix_action: "1) Validate paths; 2) Use chroot"
severity: high
---

# Path Traversal

## Pattern

PRs introducing path traversal vulnerability get rejected.

## How to Avoid

1. Validate paths
2. Use chroot
