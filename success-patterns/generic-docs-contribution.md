---
type: Success Pattern
key: generic-docs-contribution
description: "Documentation-only PRs have high merge rate across all repos"
tags: [generic, docs, high-success-rate]
created: 2026-07-29
source_url: https://github.com/zsxh1990/pr-genius/tree/main/success-patterns/generic-docs-contribution.md
updated: 2026-08-01
confidence: medium
---

# Generic Documentation Contribution

## Pattern

Documentation-only PRs (fixing typos, improving README, adding examples) have the highest merge rate across all repository types.

## Success Signals

- `is_docs_only: true`
- Small diff (< 50 lines)
- No code changes
- Clear, descriptive title

## Evidence

- awesome-mcp-servers: All listing PRs are docs-only, merge < 24h
- fastmcp: Docs PRs merge faster than code PRs
- maigret: Site data updates are considered docs, merge quickly

## Applicability

Works for: large, medium, small, and generic repos
