---
type: Repo Profile
title: microsoft/markitdown PR 模式分析
description: 126k-star Python document-to-markdown converter with Microsoft-style review process
repo: microsoft/markitdown
url: https://github.com/microsoft/markitdown
star: 126000
language: Python
zsxh_pr_count: 0
status: research-only
analyzed_at: 2026-07-09
data_source: cross-validation report (37 PR sample)
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: true
  require_cla: true
  require_issue_first: true
  ai_policy: neutral
  maintainer_vibe: slow
  bot_review: true
  ci_first_run_needs_approval: true
  default_branch: main
  response_time_h_median: 168
  external_merge_rate: 0.22
tags:
  - repo-profile
  - python
  - document-processing
  - microsoft
  - strict-review
  - large-repo
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/microsoft/markitdown/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/microsoft/markitdown/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/microsoft/markitdown/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/microsoft/markitdown/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/microsoft/markitdown/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/microsoft/markitdown/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **Microsoft 风格**: 有 CLA 要求，贡献者需签署 Microsoft Contributor License Agreement
- **响应慢**: 中位数 ~168h（约 1 周），Microsoft 项目 review 周期普遍较长
- **外部合并率约 22%**: 核心功能由内部团队主导，外部 PR 多为格式支持扩展
- **CI 门控严格**: 首次贡献者 CI 需批准，且有 CLA check

## 反模式

- **未签 CLA**: 未签署 CLA 的 PR 会被 bot 标记并阻塞，需要先完成 CLA 签署
- **Issue 缺失**: 建议先开 Issue 讨论方案，直接提大 PR 容易被要求重新设计
- **缺乏测试**: 新增格式支持必须附带测试用例和样本文件

## 建议

1. **先签 CLA**: 在提 PR 之前确保 Microsoft CLA 已签署
2. **开 Issue 讨论**: 描述你要添加的格式支持或修复的 bug
3. **附带样本文件和测试**: 新格式支持需要提供测试用的样本文档
4. **耐心等待**: Microsoft 项目 review 周期长，不要催促
5. **遵循代码规范**: 项目有 linter 和 formatter 配置，提交前本地检查
