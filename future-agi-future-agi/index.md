---
type: Repo Profile
title: future-agi/future-agi PR 模式分析
description: future-agi observability 仓 PR 模式 + zsxh1990 PR #778 + 克莱恩亲自 check-in
repo: future-agi/future-agi
url: https://github.com/future-agi/future-agi
star: 1266
language: Python
zsxh_pr_count: 1
status: in-flight-priority
analyzed_at: 2026-07-01
priority_reason: 克莱恩 2026-06-28 14:25 GMT+8 亲自发了 friendly check-in
tags:
  - repo-profile
  - observability
  - ai-tracing
  - priority-followup
related:
  - ./pr-778-span-list-without-project-id.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: slow
  bot_review: entelligence
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 168  # 3-7 天
  merge_rate_30d: null
  close_keywords: []
  one_pr_friendly: false  # PR 评审慢，多 PR 风险高
misakanet_queries:
  - misakanet/lessons/contrib/friendly-checkin-template.md  # Ikalus1988 发的 friendly check-in 模板
misakanet_lessons: []
federation_status: declared-2026-07-02
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/future-agi/future-agi
  - https://api.github.com/repos/future-agi/future-agi
  - https://api.github.com/repos/future-agi/future-agi/releases/latest
  - https://api.github.com/repos/future-agi/future-agi/commits
confidence: high  # autogen from GH API; bump to medium if human-curated
last_release: 0.5.10
last_commit_sha: ee70af01
stars: 1304
---


# future-agi/future-agi

> Future AGI 是 AI 可观测性平台（tracing + evaluation）。  
> **AI 友好度**：中（entelligence-ai-pr-reviews bot 配置 = 半主动迎 AI）。  
> **zsxh1990 PR 经验**：1 个 open（#778）+ **克莱恩亲自发了 check-in**。

---

## 1. 友好度画像

- ✅ entelligence-ai-pr-reviews bot（半自动 AI review）
- ⚠️ 中型 startup，maintainer 响应 3-7 天
- ⚠️ bot review 不等于 maintainer 通过

---

## 2. zsxh1990 PR 进展（**优先级最高**）

### 🟢 #778 [feat: enable span list view without project_id](https://github.com/future-agi/future-agi/pull/778)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-04 10:55 UTC（**27 天前**） |
| 最后活动 | 2026-06-28 07:25 UTC（3 天前） |
| 状态 | open |
| +2 / -2 / 1 file | 极小 |
| entelligence review | 2 findings + 1 comment |

**关键时间线**：

| 时间 | 事件 |
|---|---|
| 2026-06-04 10:55 | PR 创建 |
| 2026-06-04 10:59 | entelligence AI 自动 review（2 findings：project=None NameError + NULL project_id EndUser lookup） |
| 2026-06-08 16:31 | zsxh1990："Good catch! Will push fix for the NULL project_id EndUser lookup issue." |
| 2026-06-08 16:38 | entelligence AI 第 2 轮 review |
| 2026-06-28 07:25 | **@Ikalus1988 亲自发 friendly check-in** |
| 2026-06-30 14:45 | 太阳 heartbeat 标记 priority |

**克莱恩 6/28 14:25 GMT+8 发的 check-in 原文**：

> "Hi team — friendly check-in on this one 🙂  
> 
> It's been a couple weeks since the PR was opened. The bot review flagged two items (project=None NameError, NULL project_id EndUser lookup) which I've addressed.  
> 
> Happy to make any adjustments if there's feedback from the human review."

---

## 3. 提 PR 方向

### 🥇 tracing 增强

- span 批量导出优化
- 跨服务 trace 关联
- cost tracking

### 🥈 evaluation 工具

- LLM-as-judge 模板
- 人工反馈接入
- benchmark dashboard

---

## 4. 优先级行动项

**下次太阳心跳时**：
1. 查看 #778 是否有 maintainer 回应
2. 如果仍无回应 → zsxh1990 再发一条："Friendly bump — any feedback on this one?"
3. 7 天无回应 → 主动 close（学 OpenClaw ClawSweeper 优雅退出）

---

## 5. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #778 案例深读](./pr-778-span-list-without-project-id.md)