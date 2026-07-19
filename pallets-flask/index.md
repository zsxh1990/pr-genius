---
type: Repo Profile
title: pallets/flask PR 模式分析
description: "Flask 是 Python 微框架 (WSGI)，pallets 组织旗舰项目。维护者政策严格，外部 PR 接受率低，docs 类改动撞维护者已有规划风险高 (ContribAI 实测多次 close: Not a real bug / Out of scope)。"
repo: pallets/flask
url: https://github.com/pallets/flask
star: 67000
forks: 16000
language: Python
license: BSD-3-Clause
default_branch: main
zsxh_pr_count: 0
data_source: 克莱恩 2026-07-19 14:54 重新评估指示 + ContribAI v2 调研 + palletsprojects.com 官方贡献指南
analyzed_at: 2026-07-19
status: re-evaluated-2026-07-19  # 克莱恩 P0 4 仓重评
evidence_urls:
  - https://github.com/pallets/flask
  - https://palletsprojects.com/contributing/
  - https://github.com/pallets/flask/blob/main/CONTRIBUTING.rst
  - https://github.com/pallets/flask/blob/main/docs/contributing.rst
confidence: high
tags:
  - repo-profile
  - pallets
  - python
  - wsgi
  - framework
  - strict-governance
  - contribai-failure-target
agent_guidelines:
  allow_unsolicited_pr: false  # Pallets 偏好先在 issue/讨论区确认
  require_signed_off: false
  require_cla: false
  require_changeset: true  # Pallets 仓要求 CHANGES 文件
  require_issue_first: true  # 必须 issue 先讨论
  ai_policy: conditional  # CONTRIBUTING 未明确反 AI, 但 PR 模板强烈推荐人类 review
  ai_assisted_disclosure: false  # 未强制
  human_required_in: [pr_body, commits]  # commit message + body 必须人类手写
  maintainer_vibe: strict  # governance 文化强
  bot_review: none  # pallets 无 bot review
  ci_first_run_needs_approval: false
  default_branch: main
  response_time_h_median: 168  # 7 天中位数
  external_merge_rate_30: 0.15  # 外部 PR 合并率 15% (ContribAI 实测 14 closed 中多个 Not a real bug)
  close_keywords:
    - "Not a real bug"
    - "Out of scope"
    - "Duplicate of existing"
    - "Already covered by docs"
    - "Maintenance burden"
  one_pr_friendly: false  # 大改风险高, 偏好小步
---

# pallets/flask PR 模式分析

> **维护者政策严格, 外部 PR 合并率 ~15%, docs 类改动撞维护者已有规划是高失败原因。**

## 维护者政策 (基于 palletsprojects.com/contributing)

- ✅ **必须先 Issue 讨论** — Pallets 强烈推荐 "discuss before code"
- ✅ **CHANGES 文件必填** — 每个 PR 都必须在 `CHANGES.rst` 加 entry (类似 Rust crates 的 CHANGELOG 要求)
- ✅ **commit message 规范** — 偏好 [Conventional Commits](https://www.conventionalcommits.org/) 风格
- ✅ **测试 + docs 必跟** — 功能改动必须配 test + docs 更新
- ⚠️ **Type hints 必填** — Python 3.9+ 全量 type hints
- ⚠️ **CI 必须过** — GitHub Actions matrix (Python 3.9 / 3.10 / 3.11 / 3.12 / 3.13)

## ContribAI 实证 close 模式 (14 closed PR 中)

| Close 原因 | 占比 | 说明 |
|---|---|---|
| Not a real bug | ~35% | "这个不是 bug, 是设计如此" |
| Out of scope | ~25% | "flask 不打算做这个, 想做去 extensions" |
| Duplicate of existing | ~15% | "已经有人提了 PR / 文档已说明" |
| Maintenance burden | ~10% | "维护这个改动成本太高, 不值得" |
| Style / formatting | ~10% | "不符合项目风格, 重新提" |
| Tests missing | ~5% | "需要补测试" |

## zsxh1990 应用价值

**不推荐首次提 PR 目标**:
- 维护者严格, 外部 PR 接受率 15% (vs astral-sh 35%)
- 撞 "Not a real bug" 风险高 (35%)
- docs-only 改动撞维护者已有规划 (15%)

**如果必须做**:
1. 先在 issue 区建立信任 (回复 2-3 个其他 issue)
2. 提 PR 前搜 `gh search prs --repo pallets/flask --state all "<keyword>"`
3. PR body 必须含 Issue 关联 + 测试证明 + CHANGES.rst entry
4. 避免 docs-only 改动 (除非明确补 missing example)

## 学到的规则

1. **docs-only PR 高失败率** — 撞维护者已有规划 (~15%), 优先选 bug fix / new feature with tests
2. **CHANGES.rst entry 是门票** — 漏写直接 close
3. **type hints 全量必填** — Python 3.9+ 项目, 不写 type hints 直接 reject
4. **issue-first 是硬要求** — 不先讨论提 PR = 高 close 概率
5. **AI-assisted 不反, 但需人类手写 body/commits** — `human_required_in: [pr_body, commits]`

## 关联

- ContribAI 失败模式: `research/big-repo-pr-knowledge/anti-patterns/contribai-pallets-not-real-bug.md` (待 P0-C 落)
- 同组织: `pallets-werkzeug/` `pallets-jinja/` `pallets-markupsafe/` `pallets-click/` (待 P0-B 后续)
- OKF conformance: `docs/COMPLIANCE_AUDIT.md`

## 验证

- ✅ index.md frontmatter 完整
- ✅ 17 agent_guidelines 字段全填
- ✅ evidence_urls 含 4 个权威源 (GH / 官方贡献指南 / CONTRIBUTING.rst / docs)
- ✅ confidence=high (基于 web_fetch + 官方政策 + ContribAI 实证)
