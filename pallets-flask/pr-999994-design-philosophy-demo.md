---
type: PR Case Study
title: "design philosophy mismatch — ContribAI demo case"
description: "Demo case showing contribai-design-philosophy-mismatch anti-pattern detection. 改动跟项目设计哲学冲突."
repo: pallets/flask
pr_number: 999994
pr_url: https://github.com/pallets/flask/pull/999994-demo
author: contribai-demo
final_status: closed-not-merged
opened_at: '2026-07-19T20:00:00Z'
closed_at: '2026-07-19T20:30:00Z'
verified_at: '2026-07-19T20:30:00Z'
evidence_urls:
  - https://github.com/pallets/flask/pull/999994-demo
  - https://raw.githubusercontent.com/zsxh1990/pr-genius/main/anti-patterns/contribai-design-philosophy-mismatch.md
confidence: high
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - demo
  - contribai
  - pallets-flask
  - design-philosophy
  - v1.4.0
links:
  - type: anti-pattern
    target: anti-patterns/contribai-design-philosophy-mismatch.md
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: +567 / -89 / 12 files
      verified_at: '2026-07-19T20:00:00Z'
      confidence: high
    response_time_h: 4.0
    maintainer_action: closed — doesn't fit our design
    bot_review: []
    blocker: null
    resolution: philosophy_mismatch
    close_reason: "This PR doesn't align with Flask's design philosophy of simplicity. Flask is intentionally minimal — this adds too much complexity. Please read our DESIGN.md first."
---

## Problem

Contributor submitted a PR that added a complex configuration system to Flask, but Flask's design philosophy is intentionally minimal and simple.

## Root Cause

Contributor did not read Flask's DESIGN.md or understand the project's core philosophy of simplicity.

## Detection

pr-genius `analyze_pr` flagged:
- `needs_preflight` signal
- Checklist item: "check_design_philosophy" with hint to read ARCHITECTURE.md / DESIGN.md

## Fix Action

1. Read project design documents: `cat ARCHITECTURE.md DESIGN.md CONTRIBUTING.md`
2. Check if change aligns with project philosophy
3. If not, redesign to fit the philosophy
4. Ask maintainer: "how does this fit your architecture?"

## Prevention

Always read design docs before contributing:
```bash
cat ARCHITECTURE.md DESIGN.md CONTRIBUTING.md
```
