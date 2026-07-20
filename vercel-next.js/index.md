---
type: Repo Profile
title: vercel/next.js PR 模式分析
repo: vercel/next.js
url: https://github.com/vercel/next.js
star: 141108
language: TypeScript
status: research-only
analyzed_at: 2026-07-15
data_source: coach smoke test analysis
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: strict
  ai_policy: true
  maintainer_vibe: neutral
  bot_review: true
  ci_first_run_needs_approval: true
  default_branch: main
tags:
  - repo-profile
  - large-repo
  - TypeScript
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/vercel/next.js/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/vercel/next.js/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/vercel/next.js/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/vercel/next.js/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/vercel/next.js/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/vercel/next.js/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **审查风格**: 大型维护团队，严格审查
- **Bot review**: 自动化 CI + 代码审查
- **合并要求**: 通常需要1-2个 approval

## 建议

1. 提 PR 前先开 Issue 讨论
2. 遵循仓库的贡献指南
3. 确保 CI 通过
