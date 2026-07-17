---
type: Repo Profile
title: microsoft/TypeScript PR 模式分析
repo: microsoft/TypeScript
url: https://github.com/microsoft/TypeScript
star: 109920
language: TypeScript
status: research-only
analyzed_at: 2026-07-15
data_source: coach smoke test analysis
agent_guidelines:
  external_merge_rate: 0.5
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
  - TypeScript
---

## PR 文化

- **审查风格**: 大型维护团队，严格审查
- **Bot review**: 自动化 CI + 代码审查
- **合并要求**: 通常需要1-2个 approval

## 建议

1. 提 PR 前先开 Issue 讨论
2. 遵循仓库的贡献指南
3. 确保 CI 通过
