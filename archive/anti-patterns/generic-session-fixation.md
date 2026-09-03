---
type: Anti-Pattern
key: generic-session-fixation
tags: [cron, scheduling, reliability]
description: "PR introducing session fixation vulnerability"
symptom: "Maintainer comments: 'Session fixation vulnerability'"
trigger_keywords:
  - "session fixation"
fix_action: "1) Regenerate session ID; 2) Invalidate old session"
created: 2026-07-29
severity: high
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-session-fixation.md
updated: 2026-08-01
confidence: medium

---

# Session Fixation

## Pattern

PRs introducing session fixation vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Regenerate session ID
2. Invalidate old session
