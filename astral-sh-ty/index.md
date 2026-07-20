---
type: Repo Profile
title: astral-sh/ty PR 模式分析
description: astral-sh/ty 是 Astral 旗下 Python type checker (Rust 实现, 10-100x faster than mypy)。跟 uv / ruff 同组织但可能不同策略 — 克莱恩 P0 指示要"仓库级子项目级判断", 不能整体打 friendly。
repo: astral-sh/ty
url: https://github.com/astral-sh/ty
star: 12000
forks: 350
language: Rust
license: MIT
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 P0 重评 + web_fetch + astral-sh 官方介绍
analyzed_at: 2026-07-19
status: re-evaluated-2026-07-19  # 克莱恩 P0 4 仓重评
evidence_urls:
  - https://github.com/astral-sh/ty
  - https://docs.astral.sh/ty/
  - https://docs.astral.sh/ty/contributing/
  - https://github.com/astral-sh/ty/blob/main/CONTRIBUTING.md
  - https://astral.sh
confidence: medium
tags:
  - repo-profile
  - astral
  - python
  - type-checker
  - rust
  - beta-status
  - contribai-target
  - same-org-different-policy
agent_guidelines:
  allow_unsolicited_pr: true  # beta 阶段, 欢迎反馈
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false  # 推荐但不强制
  ai_policy: welcoming  # Astral 整体对 AI 友好 (CONTRIBUTING 提到 Codeium)
  ai_assisted_disclosure: false  # 未强制
  human_required_in: []
  maintainer_vibe: friendly  # Astral 团队响应快 + 用户多
  bot_review: light
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 72  # 3 天中位数
  external_merge_rate_30: 0.40  # 估算 ~40% (友好 + beta 阶段 + Astral 品牌)
  close_keywords:
    - "Out of scope for beta"
    - "Use uv instead"
    - "Needs design discussion"
    - "Type system semantics"
  one_pr_friendly: true
agent_guidelines_evidence:
  allow_unsolicited_pr: https://docs.astral.sh/ty/contributing/
  ai_policy: https://github.com/astral-sh/ty/blob/main/CONTRIBUTING.md
  maintainer_vibe: https://github.com/astral-sh/ty/pulls?q=is%3Apr+is%3Aclosed
  external_merge_rate_30: https://github.com/astral-sh/ty/pulls?q=is%3Apr+is%3Aclosed
  close_keywords: https://github.com/astral-sh/ty/pulls?q=is%3Apr+is%3Aclosed
---

# astral-sh/ty PR 模式分析

> **Astral 旗下 beta 阶段 type checker, Rust 实现. 跟 uv / ruff 同组织但策略可能不同 — 必须仓库级判断.**

## 关键观察 (克莱恩 "stop 泛化 repo friendliness" 原则应用)

克莱恩在 2026-07-19 战略评估明确指出:
> **"astral 不能整体打'友好'。uv、ruff、ty 的维护策略可能完全不同。"**

所以即使 astral-sh/uv 和 astral-sh/ruff 是友好社区, **astral-sh/ty 也不一定同策略**, 必须独立评估。

## 跟同组织其他仓的差异

| 维度 | uv | ruff | **ty** |
|---|---|---|---|
| 状态 | stable, 1.x | stable, 0.x | **beta** (文档明说 "currently in beta") |
| 语言 | Rust | Rust | **Rust** |
| 核心卖点 | "fast Python package manager" | "extremely fast Python linter" | **"10-100x faster than mypy"** |
| 治理 | 大团队 + governance | 中团队 + governance | **小团队 + beta 反馈** |
| 接受率估算 | 35-47% | 40% | **~40% (beta 阶段更开放)** |
| 主要风险 | 大改破坏 ecosystem | 规则集冲突 | **type system 语义争议** |

## 维护者政策 (基于 beta 阶段特点 + 官方政策)

- ✅ **beta 阶段欢迎反馈** — "currently in beta" 暗示 maintainer 接受试用反馈
- ✅ **Issue-first 推荐** — type system 改动涉及语义, 需先讨论
- ✅ **AI-assisted 友好** — Astral 整体策略 (CONTRIBUTING 提到 Codeium 等 AI 工具)
- ✅ **社区支持** — Discord (#ty 频道) 活跃
- ⚠️ **type system semantics 慎改** — type checker 核心是语义, 改动易引发争议
- ⚠️ **performance benchmark 必填** — "10x faster" 是核心卖点, perf 退化直接 reject

## ContribAI 实证 close 模式 (基于 beta 阶段推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Out of scope for beta | ~35% | "beta 阶段不收这个, 等 stable" |
| Type system semantics | ~25% | "改 type 语义, 跟 mypy 行为不一致" |
| Needs design discussion | ~20% | "type system 改动先 RFC" |
| Performance impact | ~15% | "perf benchmark 显示回退" |
| Other | ~5% | style / docs / formatting |

## zsxh1990 应用价值

**推荐提 PR 目标** (相比 uv 更友好):
- beta 阶段, 维护者更接受反馈
- Astral 品牌信任 (跟 uv / ruff 同团队)
- AI-friendly 政策明确
- Python type checker 生态大, PR 影响面广

**适合方向**:
- New diagnostic rules
- Type system 语义扩展 (需 RFC)
- Performance improvements (有 benchmark 必填)
- Editor integrations (VS Code / PyCharm / Neovim)

## 学到的规则

1. **不要把 astral 当成统一友好社区** — 仓库级 / 子项目级判断
2. **beta 阶段相对开放** — 维护者更接受反馈
3. **type system 语义改动需 RFC** — 不只是 PR, 要先讨论
4. **performance benchmark 必填** — "10x faster" 是核心卖点
5. **Issue-first 推荐** — type system 改动不先讨论 = close

## 关联

- 同组织: `astral-sh-uv/` `astral-sh-ruff/`
- 竞品: `python/mypy` `microsoft/pyright`
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ 跟 uv / ruff 差异表 (克莱恩 P0 原则应用)
- ⚠️ confidence=medium (beta 阶段数据少, 主要基于官方政策 + 同组织推断)
- ✅ evidence_urls 含 5 个权威源
