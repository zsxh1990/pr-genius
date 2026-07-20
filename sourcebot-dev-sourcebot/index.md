---
type: Repo Profile
title: sourcebot-dev/sourcebot PR 模式分析
description: Sourcebot 仓 PR 模式 + zsxh1990 PR #1383 进展
repo: sourcebot-dev/sourcebot
url: https://github.com/sourcebot-dev/sourcebot
star: 3553
language: TypeScript
zsxh_pr_count: 1
status: in-flight
analyzed_at: 2026-07-01
tags:
  - repo-profile
  - code-search
  - ctags
  - typescript
related:
  - ./pr-1383-ctags-failure-detection.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: responsive
  bot_review: coderabbit
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48
  merge_rate_30d: null
  close_keywords: []
  one_pr_friendly: true
misakanet_queries:
  - misakanet/lessons/contrib/silent-failure-detection.md  # ctags 沉默失败检测
misakanet_lessons: []
federation_status: declared-2026-07-02
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/sourcebot-dev/sourcebot
  - https://api.github.com/repos/sourcebot-dev/sourcebot
  - https://api.github.com/repos/sourcebot-dev/sourcebot/releases/latest
  - https://api.github.com/repos/sourcebot-dev/sourcebot/commits
confidence: high  # autogen from GH API; bump to medium if human-curated
last_release: v5.0.4
last_commit_sha: 9c4780da
stars: 3563
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/sourcebot-dev/sourcebot/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/sourcebot-dev/sourcebot/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/sourcebot-dev/sourcebot/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/sourcebot-dev/sourcebot/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/sourcebot-dev/sourcebot/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/sourcebot-dev/sourcebot/pulls?q=is%3Apr+is%3Aclosed
---


# sourcebot-dev/sourcebot

> Sourcebot 是 self-hosted 代码搜索平台（替代 Sourcegraph）。  
> **AI 友好度**：中（中型 startup，CodeRabbit 已配）。  
> **zsxh1990 PR 经验**：1 个 open（#1383）。

---

## 1. 友好度画像

- ✅ CodeRabbit 自动 review 配置
- ✅ 中型 startup 风格（外部 PR 接受率较高）
- ⚠️ maintainer 数量有限（4-6 人）

---

## 2. zsxh1990 PR 进展

### 🟢 #1383 [feat: detect and surface ctags indexing failures](https://github.com/sourcebot-dev/sourcebot/pull/1383)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-28 09:23 UTC（3 天前） |
| 状态 | open |
| +60 / -6 / 2 files | 极小 PR（理想 size）|
| CodeRabbit review | 1 actionable finding |

**价值**：ctags 失败 = 用户最痛的"沉默失败"问题之一

---

## 3. 提 PR 方向

### 🥇 indexing error reporting

- 已有 #1383 基础 → 扩展：
  - LSP indexer 失败检测
  - Git clone 失败检测
  - Per-connection 错误聚合

### 🥈 search UX 改进

- query syntax 高亮
- filter UI 改进
- saved searches

### 🥉 connector 扩展

- 新增 GitLab / Bitbucket connector
- 改进 GitHub connector 速率限制处理

---

## 4. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #1383 案例深读](./pr-1383-ctags-failure-detection.md)