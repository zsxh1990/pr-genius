---
type: Repo Profile
title: modelcontextprotocol/python-sdk PR 模式分析
description: Official Python SDK for Model Context Protocol — high-traffic, fast-merge
repo: modelcontextprotocol/python-sdk
url: https://github.com/modelcontextprotocol/python-sdk
star: 23900
language: Python
license: MIT
default_branch: main
zsxh_pr_count: 2
status: active
analyzed_at: 2026-08-05
data_source: GitHub API + PR history
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  maintainer_vibe: responsive
  bot_review: true
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48
  external_merge_rate_30: 0.25
  close_keywords: ["stale", "out of scope", "duplicate"]
  one_pr_friendly: false
---

# modelcontextprotocol/python-sdk

## PR 模式

- **High-traffic**: 23.9k stars, fast-moving
- **Bot review**: Cubic AI auto-reviews all PRs
- **Merge style**: Squash merge preferred
- **CI**: 28 checks (tests on Python 3.10-3.14, Ubuntu + Windows)
- **Review time**: Usually 1-3 days for small changes

## 已提 PR

| PR | 内容 | 状态 |
|-----|------|------|
| #3246 | OAuth refresh metadata fix | ✅ CI 全绿，等 review |

## 注意事项

- PR body 要详细描述问题和修复方案
- 需要关联 issue（Fixes #NNN）
- Cubic AI review 是自动的，不需要手动触发
- License FOSSA 检查是项目级问题，不影响单个 PR

agent_guidelines_evidence:
  allow_unsolicited_pr:
    evidence_urls: ["https://github.com/modelcontextprotocol/python-sdk/pulls"]
    verified_at: "2026-08-06"
    confidence: high
  ai_policy:
    evidence_urls: ["https://github.com/modelcontextprotocol/python-sdk"]
    verified_at: "2026-08-06"
    confidence: medium
  require_signed_off:
    evidence_urls: ["https://github.com/modelcontextprotocol/python-sdk/blob/main/CONTRIBUTING.md"]
    verified_at: "2026-08-06"
    confidence: medium
