---type: Anti-Pattern
key: generic-clickjacking
tags: [cron, scheduling, reliability]
description: "PR introducing clickjacking vulnerability"
symptom: "Maintainer comments: 'Clickjacking vulnerability'"
trigger_keywords:
  - "clickjacking"
  - "ui redress"
fix_action: "1) Add X-Frame-Options; 2) Add CSP frame-ancestors"
created: 2026-07-29
severity: medium
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-clickjacking.md
updated: 2026-08-01
confidence: medium
---

# Clickjacking

## Pattern

PRs introducing clickjacking vulnerability get rejected.

## Applicability

Universal — applies to all repository sizes (large, medium, small).

## How to Avoid

1. Add X-Frame-Options
2. Add CSP frame-ancestors
