---
type: Success Pattern
key: large-repo-bug-fix-with-test
description: "Bug fixes with regression tests merge faster"
tags: [large-repo, bug-fix, test, regression]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/large-repo-bug-fix-with-test.md
updated: 2026-08-01
confidence: medium
---

# Large Repo: Bug Fix with Regression Test

## Pattern

Bug fixes that include a regression test merge faster because they prove the fix works and prevent future regressions.

## Success Strategy

1. Reproduce the bug
2. Write a failing test
3. Fix the bug
4. Verify test passes

## Evidence

- facebook/react: bug fixes require tests
- vercel/next.js: regression tests expected
- rust-lang/rust: bug fixes need regression tests

## Applicability

All large repos
