---
type: Repo Profile
title: goreleaser/nfpm PR 模式分析
description: 1.2k-star Go packaging tool with bot auto-merge and lean review process
repo: goreleaser/nfpm
url: https://github.com/goreleaser/nfpm
star: 1200
language: Go
zsxh_pr_count: 0
status: research-only
analyzed_at: 2026-07-09
data_source: cross-validation report (37 PR sample)
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: true
  require_cla: false
  require_issue_first: false
  ai_policy: neutral
  maintainer_vibe: responsive
  bot_review: true
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 12
  external_merge_rate: 0.60
tags:
  - repo-profile
  - go
  - packaging
  - small-repo
  - bot-auto-merge
---

## PR 文化

- **Bot 自动合并**: 配置了自动合并 bot，满足条件的 PR 可自动合并
- **响应快**: 中位数 ~12h，小型项目维护者响应迅速
- **外部合并率高**: 约 60%，对社区贡献非常友好
- **DCO 签名**: 要求 Developer Certificate of Origin 签名

## 反模式

- **未签名提交**: 缺少 DCO sign-off 的 PR 会被 bot 标记
- **Go 风格不符**: 必须通过 `golangci-lint` 检查
- **缺少测试**: Go 项目对测试覆盖要求高

## 建议

1. **签名提交**: `git commit -s` 确保 DCO sign-off
2. **本地 lint**: 提交前运行 `golangci-lint run`
3. **测试覆盖**: 新功能必须有对应的单元测试
4. **小步提交**: 项目小而精，每个 PR 聚焦单一改动
5. **参考现有 PR**: 学习已合并 PR 的格式和风格
