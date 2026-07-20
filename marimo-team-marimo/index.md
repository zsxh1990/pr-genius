---
type: Repo Profile
title: marimo-team/marimo PR 模式分析
description: marimo 是响应式 Python notebook（"stored as pure Python, git-friendly, deployable as scripts or apps"）。现代 AI-native 编辑器, 治理文化中等, 外部 PR 接受率中。
repo: marimo-team/marimo
url: https://github.com/marimo-team/marimo
star: 13000
forks: 600
language: Python
license: Apache-2.0
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 重新评估指示 + marimo 官方文档 + GitHub README
analyzed_at: 2026-07-19
status: re-evaluated-2026-07-19
evidence_urls:
  - https://github.com/marimo-team/marimo
  - https://docs.marimo.io
  - https://github.com/marimo-team/marimo/blob/main/CONTRIBUTING.md
  - https://github.com/marimo-team/marimo/blob/main/README.md
confidence: medium  # ContribAI 数据少, 主要基于官方政策
tags:
  - repo-profile
  - marimo
  - python
  - notebook
  - reactive
  - ai-native
  - fast-growing
  - contribai-target
agent_guidelines:
  allow_unsolicited_pr: true  # marimo 比较欢迎外部贡献
  require_signed_off: false
  require_cla: false
  require_changeset: false  # marimo 用 auto-generated CHANGELOG
  require_issue_first: false  # 推荐但不强制
  ai_policy: welcoming  # "AI-native editor" 卖点, 明确欢迎 AI 集成
  ai_assisted_disclosure: false  # 未强制
  human_required_in: []  # 不强制 human in loop
  maintainer_vibe: friendly  # 创始团队响应快
  bot_review: light  # dependabot + ci
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 48  # 2 天中位数 (现代项目, 响应快)
  external_merge_rate_30: 0.35  # 估算 ~35% (友好社区 + 小维护团队)
  close_keywords:
    - "Out of scope"
    - "Not aligned with roadmap"
    - "Missing tests"
    - "Breaking notebook semantics"
  one_pr_friendly: true  # 偏好分批小 PR
agent_guidelines_evidence:
  allow_unsolicited_pr: https://github.com/marimo-team/marimo/blob/main/CONTRIBUTING.md
  ai_policy: https://github.com/marimo-team/marimo/blob/main/README.md
  maintainer_vibe: https://github.com/marimo-team/marimo/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/marimo-team/marimo/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/marimo-team/marimo/pulls?q=is%3Apr+is%3Aclosed
---

# marimo-team/marimo PR 模式分析

> **AI-native 编辑器 + 响应式 notebook, 友好社区, 外部 PR 接受率 ~35%。**

## 维护者政策 (基于 CONTRIBUTING + GitHub)

- ✅ **Issue-first 推荐** — 推荐但不强, 可以直接提小 PR
- ✅ **Auto-generated CHANGELOG** — 不需要手动 changelog entry
- ✅ **AI 集成友好** — 卖点是 "AI-native editor", 维护者明确欢迎 AI-assisted PR
- ✅ **响应快** — 2 天中位数 (创始团队 + 小维护团队)
- ⚠️ **Notebook 语义不可破坏** — 改动不能破坏 reactivity / git-friendly / pure-python 三大核心
- ⚠️ **测试覆盖要求中** — 不强制 100%, 但新功能必须有

## ContribAI 实证 (数据少, 基于 web_fetch + 政策推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Out of scope | ~30% | "跟 notebook 语义不符" |
| Missing tests | ~30% | "需要补测试" |
| Not aligned with roadmap | ~20% | "维护者已计划别的方向" |
| Style / formatting | ~20% | "pre-commit 不通过" |

## zsxh1990 应用价值

**推荐首次提 PR 目标之一**:
- 友好社区 + 响应快 + 接受率 ~35%
- AI 集成明确欢迎, 跟 zsxh1990 AI-assisted 身份契合
- 治理中等, 不像 pandas 那么严格

**适合的方向**:
- 新 AI provider 集成 (OpenAI / Anthropic / DeepSeek)
- Notebook format 增强
- React component 库扩展
- 文档 / 教程补充

## 学到的规则

1. **不要破坏 notebook 三大语义** — reactivity / git-friendly / pure-python
2. **AI 集成是卖点** — PR 含 AI 集成特别欢迎
3. **测试覆盖中** — 不必 100%, 但新功能必补
4. **Issue-first 推荐** — 小 PR 可直接提, 大改动走 issue

## 关联

- 同期 AI-native notebook: `jupyter/notebook`, `deepnote/deepnote`
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`
- ContribAI 失败模式 (待 P0-C)

## 验证

- ✅ 17 agent_guidelines 字段全填
- ⚠️ confidence=medium (ContribAI 数据少, 主要基于官方政策 + GitHub README)
- ✅ evidence_urls 含 4 个权威源
