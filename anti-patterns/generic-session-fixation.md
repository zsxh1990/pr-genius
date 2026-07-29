---
type: Anti-Pattern
key: generic-session-fixation
description: "PR introducing session fixation vulnerability"
symptom: "Maintainer comments: 'Session fixation vulnerability'"
trigger_keywords:
  - "session fixation"
fix_action: "1) Regenerate session ID; 2) Invalidate old session"
severity: high
---

# Session Fixation

## Pattern

PRs introducing session fixation vulnerability get rejected.

## How to Avoid

1. Regenerate session ID
2. Invalidate old session
