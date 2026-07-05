---
type: PR Case Study
title: harbor PR #2121 - make litellm and datasets optional dependencies
description: zsxh1990 在 harbor 提的 litellm/datasets 可选依赖 PR，Vercel + Devin 反馈
pr_number: 2121
pr_url: https://github.com/harbor-framework/harbor/pull/2121
repo: harbor-framework/harbor
author: zsxh1990
status: open
opened_at: 2026-06-28
last_activity: 2026-06-28
tags:
  - pr-case-study
  - open
  - optional-deps
  - vercel-preview
  - devin-reviewed
related:
  - ../index.md
verified_at: "2026-07-05T04:12:46Z"
evidence_urls:
  - https://github.com/harbor-framework/harbor/pull/2121
  - https://api.github.com/repos/harbor-framework/harbor/pulls/2121
  - https://api.github.com/repos/harbor-framework/harbor/pulls/2121/files
  - https://api.github.com/repos/harbor-framework/harbor/issues/2121/comments
  - https://api.github.com/repos/harbor-framework/harbor/pulls/2121/reviews
  - https://api.github.com/repos/harbor-framework/harbor/pulls/2121/commits
confidence: high
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+57 / -23 / 6 files"
      verified_at: "2026-06-28T09:14:50Z"
      evidence_urls:
        - https://github.com/harbor-framework/harbor/pull/2121/files
        - https://github.com/harbor-framework/harbor/pull/2121
        - https://api.github.com/repos/harbor-framework/harbor/pulls/2121/commits
      confidence: high  # PR created_at from GH API; commits at c240a2b2
    response_time_h: 0.1
    maintainer_action: null
    bot_review:
      - "vercel[bot]: 部署预览需 maintainer 授权"
      - "github-actions[bot]: diff viewer"
      - "devin-ai-integration[bot]: 2 findings (待修)"
    timestamp: "2026-06-28T09:14:00Z"
close_decision:
  status: pending
  reason: "auto-migrated from v0.1; pending close decision by zsxh1990"
  decided_at: null
  actor: zsxh1990
final_status: open
opened_at: "2026-06-28T09:14:00Z"
last_activity: "2026-06-28T09:20:00Z"
next_action: "修 Devin 2 findings，等 maintainer 触发 Vercel 预览"
---

# harbor PR #2121: feat: make litellm and datasets optional dependencies

> zsxh1990 在 [harbor-framework/harbor#2121](https://github.com/harbor-framework/harbor/pull/2121) 的可选依赖 PR。  
> **状态**：🟢 open（3 天）  
> **核心价值**：建立 harbor 可选依赖模式（litellm/datasets → extras_require）。

---

## PR 内容

**问题**：harbor 默认安装 `litellm`（~150MB）+ `datasets`（~500MB），但很多场景只用其一  
**方案**：
- `pip install harbor` - 最小安装
- `pip install harbor[llm]` - 加 litellm
- `pip install harbor[data]` - 加 datasets
- `pip install harbor[all]` - 全装

**规模**：+57 / -23 / 6 files（小而精）

---

## 反馈时间线

| 时间 | 事件 |
|---|---|
| 2026-06-28 09:14 | PR 创建 + Vercel bot 通知（需 maintainer 授权） |
| 2026-06-28 09:15 | github-actions bot diff viewer 链接 |
| 2026-06-28 09:20 | @devin-ai-integration[bot] 自动 review，2 findings |

---

## Devin AI 反馈（待深读）

Devin 找到 2 个 potential issues（细节未读，zsxh1990 未提 amend）。  
**特征**：Devin 是 harbor 官方接入的 AI review = **他们的反馈大概率需要处理**。

---

## 下一步

- ✅ Vercel 预览等授权（maintainer 操作）
- ⚠️ Devin findings 待修
- ❌ maintainer 真实 review 未开始

---

## 关联文档

- [harbor 仓 Profile](../index.md)
- [OKF bundle 根入口](../index.md)