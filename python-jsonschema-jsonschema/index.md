---
type: Repo Profile
title: python-jsonschema/jsonschema PR 模式分析
description: 4.5k-star Python JSON Schema implementation with bot auto-merge and mature review process
repo: python-jsonschema/jsonschema
url: https://github.com/python-jsonschema/jsonschema
star: 4500
language: Python
zsxh_pr_count: 0
status: research-only
analyzed_at: 2026-07-09
data_source: cross-validation report (37 PR sample)
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_issue_first: true
  ai_policy: neutral
  maintainer_vibe: selective-responsive
  bot_review: true
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 96
  external_merge_rate: 0.40
tags:
  - repo-profile
  - python
  - json-schema
  - small-repo
  - bot-auto-merge
---

## PR 文化

- **Bot 自动合并**: 满足 CI 通过 + 维护者 approve 条件后可自动合并
- **响应时间中等**: 中位数 ~96h，维护者 Julian 是单人维护，需耐心等待
- **外部合并率约 40%**: spec 相关 PR 合并率高，功能 PR 需充分讨论
- **Issue 优先**: 建议先开 Issue 讨论，尤其是涉及 API 变更的 PR

## 反模式

- **无 Issue 讨论**: 大的功能改动无 Issue 讨论直接提 PR 容易被拒
- **忽略 spec**: JSON Schema 实现必须严格遵循 spec，不接受"方便"的偏差
- **测试不足**: 项目有完善的测试体系，新功能必须有测试

## 建议

1. **先开 Issue**: 讨论你的改动是否符合项目方向
2. **严格遵循 spec**: JSON Schema 规范是第一优先级
3. **完善测试**: 项目使用 pytest，测试覆盖是合并的硬性要求
4. **文档同步**: API 变更需同步更新文档
5. **小步提交**: 维护者偏好小而精的改动
