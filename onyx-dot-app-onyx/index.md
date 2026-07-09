---
type: Repo Profile
title: onyx-dot-app/onyx PR 模式分析
description: 30k-star Python AI search platform with active owner self-submissions and good external merge rate
repo: onyx-dot-app/onyx
url: https://github.com/onyx-dot-app/onyx
star: 30000
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
  ai_policy: welcoming
  maintainer_vibe: responsive
  bot_review: false
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 36
  external_merge_rate: 0.42
tags:
  - repo-profile
  - python
  - ai-search
  - welcoming
  - medium-repo
---

## PR 文化

- **OWNER 自提交为主**: 大量 PR 由核心团队成员提交，但外部贡献也受欢迎
- **响应快**: 中位数 ~36h，维护者活跃度高
- **外部合并率约 42%**: 在同等规模项目中属于较高水平
- **CI 无门控**: 首次贡献者 CI 自动运行，无额外批准步骤

## 反模式

- **大 PR**: 项目代码量大，PR 过大会增加 review 难度
- **缺乏上下文**: PR 描述不够详细时，维护者可能要求补充
- **数据库迁移**: 涉及 schema 变更的 PR 需要特别谨慎

## 建议

1. **直接提 PR**: 不强制要求先开 Issue，但建议在 PR 描述中说明动机
2. **关注 good-first-issue**: 项目有标记的入门级 issue
3. **本地测试**: 确保 `docker-compose` 环境能正常运行后再提交
4. **小步迭代**: 聚焦单一功能或修复
5. **文档贡献**: 改进文档是快速建立信任的方式
