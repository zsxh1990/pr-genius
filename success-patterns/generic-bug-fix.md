---
type: Success Pattern
key: generic-bug-fix
description: "Bug fixes with clear reproduction steps have high merge rate"
tags: [generic, bug-fix, high-success-rate]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-bug-fix.md
updated: 2026-08-01
confidence: medium
---

# Generic Bug Fix Contribution

## Pattern

Bug fixes with clear problem description, root cause analysis, and verification steps have high merge rate.

## Success Signals

- `is_bug_fix: true`
- `has_issue_link: true`
- Small-medium diff (< 200 lines)
- Includes test or verification steps

## Evidence

- maigret #2908: SSRF fix (+188/-1), merged quickly
- HolmesGPT #2322: HTTP proxy fix (+54/-1), merged in 1 day
- honcho #949: Test throughput fix (+148/-23), merged same day

## Applicability

Works for: all repo sizes
