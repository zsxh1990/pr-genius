---
type: Repo Profile
title: facebook/react PR 模式分析
repo: facebook/react
url: https://github.com/facebook/react
star: 246498
language: JavaScript
status: research-only
analyzed_at: 2026-07-15
data_source: coach smoke test analysis
agent_guidelines:
  external_merge_rate: 0.37
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: strict
  ai_policy: true
  maintainer_vibe: restrictive
  bot_review: true
  ci_first_run_needs_approval: true
  default_branch: main
tags:
  - repo-profile
  - large-repo
  - JavaScript
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/facebook/react/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/facebook/react/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/facebook/react/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/facebook/react/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/facebook/react/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/facebook/react/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **审查风格**: 大型维护团队，严格审查
- **Bot review**: 自动化 CI + 代码审查
- **合并要求**: 通常需要1-2个 approval

## 建议

1. 提 PR 前先开 Issue 讨论
2. 遵循仓库的贡献指南
3. 确保 CI 通过
