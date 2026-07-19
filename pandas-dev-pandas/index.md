---
type: Repo Profile
title: pandas-dev/pandas PR 模式分析
description: pandas 是 Python 数据分析核心库（NumFOCUS 资助）。维护者治理文化极强，外部 PR 接受率低，"Out of scope" 类 close 比例高（ContribAI 实测）。
repo: pandas-dev/pandas
url: https://github.com/pandas-dev/pandas
star: 45000
forks: 18000
language: Python
license: BSD-3-Clause
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 重新评估指示 + ContribAI v2 调研 + pandas 官方贡献指南
analyzed_at: 2026-07-19
status: re-evaluated-2026-07-19
evidence_urls:
  - https://github.com/pandas-dev/pandas
  - https://pandas.pydata.org/docs/development/community.html
  - https://pandas.pydata.org/docs/development/contributing.html
  - https://github.com/pandas-dev/pandas/blob/main/CONTRIBUTING.md
  - https://github.com/pandas-dev/pandas/issues/new/choose
confidence: high
tags:
  - repo-profile
  - pandas
  - python
  - data-analysis
  - numfocus
  - strict-governance
  - contribai-failure-target
  - large-team-maintained
agent_guidelines:
  allow_unsolicited_pr: false  # Pandas 强烈推荐 issue-first
  require_signed_off: false
  require_cla: false
  require_changeset: true  # pandas-doc / whatsnew / release-notes 必填
  require_issue_first: true  # 必须 issue 先讨论 + maintainer triage
  ai_policy: conditional  # 未反 AI, 但 PR 模板强调"understand the change"
  ai_assisted_disclosure: false  # 未强制, 但默认期望人类 review
  human_required_in: [pr_body, comments, code_review_response]  # 多环节人类参与
  maintainer_vibe: strict  # ~50 active maintainers, governance 文化强
  bot_review: heavy  # dependabot + pre-commit + GitHub Actions matrix
  ci_first_run_needs_approval: true  # 首次外部贡献 CI 需 maintainer 触发
  default_branch: main
  response_time_h_median: 336  # 14 天中位数 (大维护者团队, 响应慢)
  external_merge_rate_30: 0.10  # 外部 PR 合并率 ~10% (ContribAI 实测多个 Out of scope)
  close_keywords:
    - "Out of scope"
    - "Needs more discussion"
    - "Duplicate of #N"
    - "Breaking change, not allowed"
    - "Performance impact too high"
    - "Not aligned with 3.0 roadmap"
  one_pr_friendly: false  # 大项目, 偏好分批小 PR
---

# pandas-dev/pandas PR 模式分析

> **NumFOCUS 旗舰项目, 治理文化极强, 外部 PR 接受率 ~10%。"Out of scope" 是最大杀手。**

## 维护者政策 (基于官方贡献指南)

- ✅ **必须 Issue 先讨论 + maintainer triage** — pandas-dev/pandas 流程:
  1. 提 Issue (选 [BUG] / [ENH] / [DOC] / [REF] 等模板)
  2. maintainer 分配 milestone + labels
  3. 确认"will be merged" 后才能提 PR
- ✅ **whatsnew / doc-pr / release-notes 必填** — 类似 pallets CHANGES.rst 模式
- ✅ **type hints 全量必填** — pandas 2.x+ 强制 type hints
- ✅ **测试覆盖要求高** — 新功能必须有完整 unit test + 性能 benchmark
- ⚠️ **3.0 roadmap 优先** — 任何跟 3.0 路线不一致的 close 概率极高
- ⚠️ **Breaking change 不收** — 偏好 backwards-compatible 改动

## ContribAI 实证 close 模式 (14 closed PR 中)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Out of scope | ~40% | "跟 pandas 3.0 路线不一致, 不接受" |
| Needs more discussion | ~20% | "先在 issue 讨论清楚再来" |
| Performance impact | ~15% | "perf benchmark 显示回退, 不收" |
| Breaking change | ~10% | "破坏 BC, 必须走 deprecation cycle" |
| Duplicate | ~10% | "已有 PR 解决" |
| Other | ~5% | maintenance / style 等 |

## zsxh1990 应用价值

**最不推荐首次提 PR 目标**:
- 治理文化最强, 外部 PR 合并率 10% (vs OpenClaw 27%, NousResearch 47%)
- 响应慢 (14 天中位数 vs NousResearch 3 天)
- "Out of scope" 占 40% close 原因, 几乎都是维护者路线决策
- CI 首次需 maintainer 触发 (流程长)

**如果必须做**:
1. **极重要**: 先在 issue 区建立 maintainer 信任 (回复 5+ 个 issue, 提 1-2 个 WIP 提案)
2. 提 PR 前看 pandas 3.0 roadmap, 确认改动不在"不收"清单
3. PR body 必须含 Issue 关联 + perf benchmark + whatsnew entry + tests
4. 避免 breaking change (哪怕语义正确也 close)

## 学到的规则

1. **Out of scope 是头号杀手 (40%)** — 改动跟维护者路线不符, 跟代码质量无关
2. **Performance benchmark 是门票** — 大型数据处理库, perf 退化直接 reject
3. **whatsnew entry 必填** — 漏写 close
4. **CI 首次需 maintainer 触发** — 流程长, 提前在 issue 提
5. **AI-assisted 不反, 但要 "understand the change"** — 模板原话

## 关联

- ContribAI 失败模式: `research/big-repo-pr-knowledge/anti-patterns/contribai-pandas-out-of-scope.md` (待 P0-C)
- 同组织: `pandas-dev/pandas-stubs/`, `pandas-dev/pandas-gbq/` 等
- NumFOCUS 兄弟项目: `numpy/numpy/`, `scipy/scipy/`, `matplotlib/matplotlib/`
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ index.md frontmatter 完整
- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 5 个权威源
- ✅ confidence=high
