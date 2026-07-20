---
type: Repo Profile
title: harbor-framework/harbor PR 模式分析
description: Harbor Framework 仓 PR 模式 + zsxh1990 PR #2121 进展
repo: harbor-framework/harbor
url: https://github.com/harbor-framework/harbor
star: 2827
language: Python
zsxh_pr_count: 1
status: in-flight
analyzed_at: 2026-07-01
tags:
  - repo-profile
  - ai-agent-framework
  - python
  - litellm
related:
  - ./pr-2121-optional-deps.md
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
  bot_review: devin
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 24  # startup 风格
  merge_rate_30d: null
  close_keywords: []
  one_pr_friendly: true
misakanet_queries:
  - misakanet/lessons/contrib/devin-ai-review-bot.md  # Harbor 接入 Devin AI review 经验
misakanet_lessons: []
federation_status: declared-2026-07-02
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/harbor-framework/harbor
  - https://api.github.com/repos/harbor-framework/harbor
  - https://api.github.com/repos/harbor-framework/harbor/releases/latest
  - https://api.github.com/repos/harbor-framework/harbor/commits
confidence: high  # autogen from GH API; bump to medium if human-curated
last_release: v0.17.1
last_commit_sha: 1d6c3851
stars: 2959
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/harbor-framework/harbor/blob/main/CONTRIBUTING.md
  require_issue_first: https://github.com/harbor-framework/harbor/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/harbor-framework/harbor/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/harbor-framework/harbor/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/harbor-framework/harbor/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/harbor-framework/harbor/pulls?q=is%3Apr+is%3Aclosed
---


# harbor-framework/harbor

> Harbor 是 AI agent 框架（LiteLLM + datasets）。  
> **AI 友好度**：高（Vercel 部署 + Devin AI 接入 = 主动迎 AI 工具链）。  
> **zsxh1990 PR 经验**：1 个 open（#2121），刚开 2 天。

---

## 1. 友好度画像

- ✅ **Vercel 集成**（PR 创建即触发部署预览）
- ✅ **Devin AI 自动 review**（主动接入 AI review bot）
- ✅ 大型 startup 风格（外部 PR 接受率高）
- ⚠️ 模块化重构期（依赖解耦，PR 空间大）

---

## 2. zsxh1990 PR 进展

### 🟢 #2121 [feat: make litellm and datasets optional dependencies](https://github.com/harbor-framework/harbor/pull/2121)

| 维度 | 数据 |
|---|---|
| 创建 | 2026-06-28 09:14 UTC（**3 天前**） |
| 状态 | open |
| +57 / -23 / 6 files | 小而精 |
| Vercel 部署 | 需 maintainer 授权 |
| Devin review | 2 findings |

**关键反馈**：
- @vercel[bot] 触发部署预览
- @devin-ai-integration[bot] 找到 2 个潜在 issue（待深读）
- 无 maintainer 评论

---

## 3. 提 PR 方向

### 🥇 optional dependencies 模式（已铺路）

- harbor 当前默认安装所有 deps（litellm + datasets 都很重）
- #2121 已拆 litellm + datasets → extras_require
- 后续可拆：`harbor[observability]` / `harbor[tracing]` / `harbor[vectordb]`

### 🥈 LiteLLM provider 扩展

- harbor 用 litellm 统一 LLM 调用
- 加新 provider（Ollama、vLLM、Together）只需 litellm 配置，无需新代码

### 🥉 agent runtime 改进

- 工具调用追踪
- Token usage metrics
- Async batching

---

## 4. SOP

| 维度 | harbor 特色 |
|---|---|
| CI | Vercel 预览 + GitHub Actions |
| Review | Devin AI + 人工 |
| Test | pytest + Vercel preview 验证 |
| 部署 | merge → Vercel 自动部署 |

---

## 5. 关联文档

- [OKF bundle 根入口](../index.md)
- [PR #2121 案例深读](./pr-2121-optional-deps.md)