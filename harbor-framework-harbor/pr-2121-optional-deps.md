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