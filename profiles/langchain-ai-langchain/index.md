---
type: Repo Profile
title: langchain-ai/langchain PR 模式分析
description: 129k-star Python AI framework with strict maintainer review and AI-generated PR policy enforcement
repo: langchain-ai/langchain
url: https://github.com/langchain-ai/langchain
star: 129000
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
  ai_policy: restrictive
  maintainer_vibe: selective-responsive
  bot_review: true
  ci_first_run_needs_approval: true
  default_branch: main
  response_time_h_median: 72
  external_merge_rate: 0.18
tags:
  - repo-profile
  - python
  - ai-framework
  - strict-review
  - ai-policy-violation
  - large-repo
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/langchain-ai/langchain/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/langchain-ai/langchain/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/langchain-ai/langchain/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/langchain-ai/langchain/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/langchain-ai/langchain/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/langchain-ai/langchain/pulls?q=is%3Apr+is%3Aclosed
---

## PR 文化

- **合并率低**: 外部 PR 合并率约 18%，大量 PR 被关闭或搁置
- **响应时间**: 中位数 ~72h，维护团队以核心成员为主，外部贡献需等待排期
- **Issue 优先**: 强烈倾向先有 Issue 再提 PR，无 Issue 的 PR 大概率被忽略
- **CI 门控**: 首次贡献者 CI 需维护者批准后才运行

## 反模式

- **AI 生成 PR 标记 `ai-policy-violation`**: 维护者会主动检测并标记疑似 AI 生成的 PR，包括泛化描述、无上下文的批量修复
- **缺少 Issue 链接 `missing-issue-link`**: PR 未关联对应 Issue 时，机器人会自动评论要求补充
- **过大的 PR**: langchain 生态鼓励小步迭代，大 PR 容易被要求拆分后重新提交

## 建议

1. **必须先开 Issue**，描述问题或 feature proposal，等维护者确认后再提 PR
2. **避免纯 AI 生成的贡献**：确保 PR 描述包含具体的使用场景和个人经验
3. **小步提交**：每个 PR 聚焦单一改动，便于 review
4. **遵循 CONTRIBUTING.md**：严格遵守代码风格、测试覆盖要求
5. **耐心等待**：大型项目 review 周期长，不要频繁 @ 维护者
