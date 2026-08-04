---
type: Success Pattern
key: generic-test-addition
description: "Test additions are low-risk and welcome in most repos"
tags: [generic, test, low-risk]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-test-addition.md
updated: 2026-08-01
confidence: medium
---

# Generic Test Addition Contribution

## Pattern

Adding tests (especially for existing code) is low-risk and welcomed by maintainers.

## Success Signals

- `is_test_only: true` or `is_docs_only: false` with `additions > deletions`
- No production code changes
- Improves coverage

## Evidence

- fastmcp #293: +289 lines of tests, merged
- python-sdk #3093: Test additions for non-2xx handling, CI green

## Applicability

Works for: large, medium, small repos with test infrastructure
