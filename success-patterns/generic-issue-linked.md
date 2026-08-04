---
type: Success Pattern
key: generic-issue-linked
description: "PRs linked to issues have higher merge rate"
tags: [generic, issue-link, best-practice]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-issue-linked.md
updated: 2026-08-01
confidence: medium
---

# Issue-Linked PRs Have Higher Success Rate

## Pattern

PRs that reference an issue (Fixes #NNN, Closes #NNN) have higher merge rate because:
1. Problem is already discussed and validated
2. Maintainer expects the fix
3. Clear motivation for the change

## Evidence

- maigret #2917: Closes #2916, CI green, waiting for review
- python-sdk #3093: Closes #3091, CI green, waiting for review
- HolmesGPT #2305: Closes #2297, has conflicts

## Applicability

Works for: all repo sizes, especially medium and large repos with issue templates
