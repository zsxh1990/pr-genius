---
type: Anti-Pattern
key: generic-no-dco
description: "Repos requiring DCO reject PRs without Signed-off-by"
tags: [generic, anti-pattern, dco]
created: 2026-07-29
trigger_keywords:
  - "missing dco"
  - "no dco"
  - "signed-off-by"
  - "dco check failed"
  - "dco fail"
  - "dco sign-off"
source_url: https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns/generic-no-dco.md
updated: 2026-08-01
confidence: medium
---

# Repos Reject PRs Without DCO Sign-Off

## Pattern

PRs to repos requiring DCO (Developer Certificate of Origin) get rejected if commits lack `Signed-off-by` line.

## How to Avoid

1. Always use `git commit -s` to add Signed-off-by
2. Check repo's CONTRIBUTING.md for DCO requirement
3. Use `git commit --amend -s` to add sign-off to last commit

## Applicability

All repository sizes where DCO is enforced via CI.
