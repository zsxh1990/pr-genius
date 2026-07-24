---
type: Repo Profile
title: yt-dlp/yt-dlp PR 模式分析
description: 166k-star Python video downloader with community-driven review and strict AI-generated content policy
repo: yt-dlp/yt-dlp
url: https://github.com/yt-dlp/yt-dlp
star: 166000
language: Python
zsxh_pr_count: 0
status: research-only
analyzed_at: 2026-07-09
data_source: cross-validation report (37 PR sample)
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: false
  ai_policy: restrictive
  maintainer_vibe: selective-responsive
  bot_review: true
  ci_first_run_needs_approval: true
  default_branch: master
  response_time_h_median: 48
  external_merge_rate: 0.35
tags:
  - repo-profile
  - python
  - video-tools
  - strict-review
  - ai-policy-violation
  - community-driven
  - large-repo
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/yt-dlp/yt-dlp/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/yt-dlp/yt-dlp/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/yt-dlp/yt-dlp/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/yt-dlp/yt-dlp/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/yt-dlp/yt-dlp/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/yt-dlp/yt-dlp/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **社区驱动**: 核心维护者人数少但活跃，社区贡献者众多，外部合并率约 35%
- **响应时间**: 中位数 ~48h，extractor 类 PR 响应更快（常有站点变更的紧迫性）
- **默认分支 `master`**: 注意不是 `main`，PR 需指向 `master`
- **CI 门控**: 首次贡献者 CI 需批准

## 反模式

- **AI 生成 PR 标记 `ai-policy-violation`**: 与 langchain 类似，维护者会拒绝明显 AI 生成的 extractor 或 bugfix
- **Extractor 质量要求高**: 站点 extractor 必须包含测试、处理 edge case，简单的 URL 解析不够
- **不要修非 bug**: yt-dlp 代码风格严格，"改进" 类 PR（重命名、重构）容易被拒

## 建议

1. **修真实 bug 或支持新站点**: 最受欢迎的 PR 类型是修复 broken extractor 或添加新站点支持
2. **附带测试**: extractor PR 必须有对应的测试用例
3. **不要用 AI 生成**: 确保代码是手写的，PR 描述体现你对代码的理解
4. **小步提交**: 一个 extractor 一个 PR
5. **检查 CONTRIBUTING.md**: 有详细的 extractor 开发指南
