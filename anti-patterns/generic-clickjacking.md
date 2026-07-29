---
type: Anti-Pattern
key: generic-clickjacking
description: "PR introducing clickjacking vulnerability"
symptom: "Maintainer comments: 'Clickjacking vulnerability'"
trigger_keywords:
  - "clickjacking"
  - "ui redress"
fix_action: "1) Add X-Frame-Options; 2) Add CSP frame-ancestors"
severity: medium
---

# Clickjacking

## Pattern

PRs introducing clickjacking vulnerability get rejected.

## How to Avoid

1. Add X-Frame-Options
2. Add CSP frame-ancestors
