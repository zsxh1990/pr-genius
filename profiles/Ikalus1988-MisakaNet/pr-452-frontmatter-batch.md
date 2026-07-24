---
type: PR Case Study
title: "MisakaNet #452 — convert 20 bare JSON frontmatter to YAML"
pr_number: 452
pr_url: https://github.com/Ikalus1988/MisakaNet/pull/452
repo: Ikalus1988/MisakaNet
author: zsxh1990
status: closed-merged
opened_at: "2026-07-12"
merged_at: "2026-07-13"
schema_version: rounds v0.5.0
verified_at: "2026-07-17T19:18:00Z"
evidence_urls:
  - https://github.com/Ikalus1988/MisakaNet/pull/452
  - https://api.github.com/repos/Ikalus1988/MisakaNet/pulls/452
  - https://api.github.com/repos/Ikalus1988/MisakaNet/pulls/452/files
  - https://api.github.com/repos/Ikalus1988/MisakaNet/issues/452/comments
  - https://api.github.com/repos/Ikalus1988/MisakaNet/pulls/452/reviews
  - https://api.github.com/repos/Ikalus1988/MisakaNet/pulls/452/commits
confidence: high
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+229 / -97 (20 files: lessons/contrib/*.md)"
    resolution: merged
    timestamp: "2026-07-12"
  - round: 2
    action: amend
    delta:
      kind: code_change
      value: "Rebase on upstream/main, resolve conflicts"
    resolution: merged
    timestamp: "2026-07-13"
---

## PR #452: frontmatter batch conversion

**Issue**: #351 — Batch fix contrib/ frontmatter

**Approach**: Python script to convert bare JSON frontmatter to proper YAML with `---` delimiters. 20 files converted.

**Outcome**: Merged after rebase. Had conflicts with upstream changes to same files.

**Key Learning**: Batch maintenance PRs need quick merge — conflicts accumulate fast. Rebase immediately after upstream changes.

**Anti-pattern**: Delayed merge → conflict accumulation (3 conflicts on rebase).

**Success Factor**: Scripted conversion (consistent), clear issue link, focused scope.
