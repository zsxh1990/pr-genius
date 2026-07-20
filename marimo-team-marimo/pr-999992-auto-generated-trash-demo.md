---
type: PR Case Study
title: "auto-generated trash detection — ContribAI demo case"
description: "Demo case showing contribai-auto-generated-trash anti-pattern detection. AI agent 生成 diff 时没清理工具产物."
repo: marimo-team/marimo
pr_number: 999992
pr_url: https://github.com/marimo-team/marimo/pull/999992-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
  - https://github.com/marimo-team/marimo/pull/999992-demo
  - https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-auto-generated-trash.md
confidence: high
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - marimo-team
  - auto-generated-trash
  - v1.4.0
links:
  - type: anti-pattern
    target: anti-patterns/contribai-auto-generated-trash.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +89 / -12 / 4 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 0.5
    maintainer_action: closed — contains generated files
    bot_review: []
    blocker: null
    resolution: generated_artifacts
    close_reason: "PR contains generated files (README.md ---, notebook.py ---). Please clean up tool artifacts before submitting."
---

## Problem

AI agent generated a PR that included tool artifacts: `README.md ---` and `notebook.py ---` files that were not real source code.

## Root Cause

AI agent's diff generation tool created artifact files with `---` suffix. The agent did not clean up these files before submitting the PR.

## Detection

pr-genius `triage_pr` flagged:
- Rule 2: "不接受生成器残留文件" (hard rejection)
- Evidence: "发现文件名含 --- 的生成器残留文件"

## Fix Action

1. Check diff for artifact files: `git diff --stat | grep "---"`
2. Remove artifact files: `rm "README.md ---" "notebook.py ---"`
3. Re-commit clean diff

## Prevention

Always check diff before submitting:
```bash
git diff --stat | grep -E "---|patch|diff"
```
