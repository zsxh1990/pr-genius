---
type: Anti-Pattern
key: generic-session-fixation
description: "PR introducing session fixation vulnerability"
symptom: "Maintainer comments: 'Session fixation vulnerability'"
trigger_keywords:
  - "session fixation"
fix_action: "1) Regenerate session ID; 2) Invalidate old session"
created: 2026-07-29
severity: high
---

# Session Fixation

## Pattern

PRs introducing session fixation vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Regenerate session ID
2. Invalidate old session
