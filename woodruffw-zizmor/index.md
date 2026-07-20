---
type: Repo Profile
title: woodruffw/zizmor PR 模式分析
description: 1k-star Python/Rust GitHub Actions security linter with strict review and AI policy enforcement
repo: woodruffw/zizmor
url: https://github.com/woodruffw/zizmor
star: 1000
language: Python/Rust
zsxh_pr_count: 0
status: research-only
analyzed_at: 2026-07-09
data_source: cross-validation report (37 PR sample)
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: true
  ai_policy: restrictive
  maintainer_vibe: selective-responsive
  bot_review: false
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48
  external_merge_rate: 0.30
tags:
  - repo-profile
  - python
  - rust
  - security
  - github-actions
  - strict-review
  - ai-policy-violation
  - small-repo
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/woodruffw/zizmor/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/woodruffw/zizmor/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/woodruffw/zizmor/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/woodruffw/zizmor/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/woodruffw/zizmor/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/woodruffw/zizmor/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **维护者是安全专家**: woodruffw 是知名安全研究者，对代码质量要求极高
- **响应时间**: 中位数 ~48h，小型项目但维护者精力有限
- **外部合并率约 30%**: 精品项目，只接受高质量贡献
- **Python/Rust 混合**: 核心逻辑用 Rust，上层用 Python，贡献需了解两者

## 反模式

- **AI 生成 PR 标记 `ai-policy-violation`**: 维护者明确反对 AI 生成的安全规则 PR，认为安全工具的质量不容妥协
- **重复 PR `duplicate-pr`**: 多人同时提相似的 rule PR 会导致冲突，需先查看已有 PR
- **无 Issue 讨论**: 安全规则的添加需要先讨论其必要性和覆盖范围

## 建议

1. **先开 Issue**: 描述你要添加的安全规则或修复的 bug，等维护者确认
2. **检查已有 PR**: 避免重复工作，查看 open PR 列表
3. **手写代码**: 不使用 AI 生成安全规则，确保每个 rule 都有明确的安全逻辑
4. **理解 GitHub Actions**: 项目专注于 GitHub Actions 安全，需熟悉其安全模型
5. **测试充分**: 安全工具的误报和漏报都是严重问题
