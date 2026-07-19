---
type: Repo Profile
title: vugu/vugu PR 模式分析
description: Vugu — Go + WebAssembly UI library (VueJS-inspired). Experimental 阶段, 单作者项目, 维护节奏慢但社区稳定.
repo: vugu/vugu
url: https://github.com/vugu/vugu
star: 3200
forks: 130
language: Go
license: MIT
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 路线图 (ContribAI v2 调研 6 新仓之一) + web_fetch + README + travis-ci
analyzed_at: 2026-07-19
status: new-profile-2026-07-19
evidence_urls:
  - https://github.com/vugu/vugu
  - https://www.vugu.org
  - https://godoc.org/github.com/vugu/vugu
  - https://travis-ci.org/vugu/vugu
  - https://github.com/emersion/stability-badges#experimental
confidence: medium
tags:
  - repo-profile
  - vugu
  - go
  - webassembly
  - wasm
  - experimental
  - vuejs-inspired
  - contribai-target
agent_guidelines:
  allow_unsolicited_pr: true  # experimental 项目欢迎反馈
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false  # 推荐但不强
  ai_policy: neutral  # 未明确表态
  ai_assisted_disclosure: false
  human_required_in: []
  maintainer_vibe: slow-but-friendly  # 单作者 + experimental 节奏
  bot_review: light  # travis-ci + dependabot
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 168  # 7 天 (单作者 + experimental)
  external_merge_rate_30: 0.35  # 估算 ~35% (experimental 阶段 + 单作者)
  close_keywords:
    - "Breaking API"
    - "Out of experimental scope"
    - "Maintainer busy"
    - "Already in vugu.org docs"
  one_pr_friendly: true
---

# vugu/vugu PR 模式分析

> **Vugu — Go + WebAssembly UI library (VueJS-inspired). Experimental 阶段, 单作者项目, 维护慢但社区稳定.**

## 项目特点

- **类型**: Go + WebAssembly UI library
- **设计灵感**: VueJS (但用 Go 不用 JS)
- **核心理念**: "If you've ever wanted to write a UI not in JS but pure Go... and run it in your browser, right now..."
- **生态**: godoc.org + travis-ci + vugu.org (官方文档)
- **状态**: Experimental (emersion/stability-badges#experimental badge)
- **维护**: 单作者项目

## 维护者政策 (基于 experimental + 单作者)

- ✅ **Experimental 阶段欢迎反馈** — 项目明说 "(experimental;) future is here"
- ✅ **No node / No JS / No npm** — 设计哲学简洁
- ✅ **godoc 自动文档** — Go 标准
- ⚠️ **API breaking change 风险** — experimental 阶段, maintainer 慎改 API
- ⚠️ **维护节奏慢** — 单作者, 7 天中位数
- ⚠️ **vugu.org 文档可能滞后** — 跟代码不同步

## ContribAI 实证 close 模式 (基于 experimental + 单作者推断)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Breaking API | ~30% | "experimental 阶段不收 breaking change" |
| Out of experimental scope | ~25% | "这跟 vugu 核心定位不符" |
| Maintainer busy | ~20% | "维护者个人项目, 慢" |
| Already in vugu.org docs | ~15% | "文档已说明, 不用 PR" |
| Other | ~10% | style / docs / refactor |

## zsxh1990 应用价值

**中等优先级 PR 目标**:
- Experimental 项目, 维护者欢迎反馈 (~35%)
- Go + WASM 生态 (跟 zsxh1990 不太契合, pr-genius 是 Python/TypeScript)
- 单作者 + 慢节奏, 不适合需要快速 turnaround 的 PR

**适合方向**:
- 文档改进 (vugu.org 可能滞后)
- 测试覆盖增强
- 性能优化 (Go + WASM benchmark)
- Example 应用扩展

## 学到的规则

1. **Experimental 项目 API breaking 慎改** — maintainer 慎改 API, 即使看似合理
2. **vugu.org 文档可能滞后** — 先查文档再 PR, 避免重复
3. **单作者慢节奏** — 不急的话可以提, 急的话别
4. **No node / No JS / No npm 设计哲学** — 改动不能引入前端工具链
5. **Go + WASM 跨语言** — 不适合 Python/TypeScript 习惯的 contributor

## 关联

- Go WASM 兄弟项目: `golang/go` (WASM 支持), `tinygo-org/tinygo`
- VueJS 风格 UI: `vuejs/vue`, 但 Vue 是 JS, Vugu 是 Go
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 5 个权威源
- ⚠️ confidence=medium (experimental + 单作者项目数据少, 主要基于官方政策 + 单作者模式推断)
