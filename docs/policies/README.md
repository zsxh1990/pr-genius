---
type: Maintainer Policy
title: Maintainer Policy Schema (MAINTAINER_POLICY.md v0.1)
description: Schema 定义 — 每个 docs/policies/<org>-<repo>.md 必须遵守的 frontmatter + body 结构. Month 2 克莱恩 2026-07-19 战略评估 P0 #1.
version: "0.1.0"
created: "2026-07-19"
conforms_to: OKF v0.1
---

# MAINTAINER_POLICY.md Schema v0.1

> **来源**: 克莱恩 2026-07-19 战略评估 Month 2 P0 #1 — 写 MAINTAINER_POLICY.md schema.
> **目的**: pr-genius `triage_pr` MCP tool 加载 `docs/policies/<org>-<repo>.md` 后用这 schema 解析出 hard/soft rules, 返回给 agent 做 policy-aware screening.

## Schema

### Frontmatter (必填)

```yaml
---
type: Maintainer Policy
repo: <org>/<repo>               # 唯一标识, 必须匹配目录名
created: YYYY-MM-DD
updated: YYYY-MM-DD
anchors: [PR#1, PR#2, ...]        # 反向链: 真实 PR 拒绝记录 PR 号
---

# <Org>/<Repo> Maintainer Policy

> 一句话政策概述 (e.g. "基于真实 PR 拒绝记录提炼的维护者政策")

## Hard Rejections (直接关闭)

### 1. <rule title>

**规则:** <rule description>

**锚点:**
- #<PR#>: <close reason excerpt from maintainer>
- #<PR#>: <another>

**原因:** <why maintainer reject>

**正确做法:** <how contributor should do instead>

---

### 2. <another rule>

(same structure)

---

## Soft Warnings (review 时关注)

### 1. <soft rule>

**规则:** <soft rule description>

**锚点:** ...

**警告:** <what triggers this soft rule>

---

## Notes

- `pr-genius` 实际硬编码了 9 个 rule 类型 (readme-rewrite / generator-residual
  / paste-patch / core-delete / docs-code / worker-api / star-fork / helpful=0 /
  bounty), 不依赖 schema 解析. Schema 的主要价值是**人类可读**
  + 给 agent 提供政策 narrative.
- `anchors` 字段是**反向证据** — 每个 rule 必须有真实 PR 拒绝记录支撑,
  否则标记为 `unverified`.
```

## 现有 Policies

| Org/Repo | 文件 | anchors | last_updated |
|---|---|---|---|
| Ikalus1988/MisakaNet | `Ikalus1988-MisakaNet.md` | 7 PRs (#491-497) | 2026-07-18 |
| openclaw/openclaw | `openclaw-openclaw.md` | 3 PRs (#93310/92872/96797) | 2026-07-19 |
| pallets/flask | `pallets-flask.md` | 4 PRs (#N) | 2026-07-19 |
| pandas-dev/pandas | `pandas-dev-pandas.md` | 5 PRs (#N) | 2026-07-19 |

## Validator 要求

`validate.py --strict` 自动检查:

1. frontmatter 4 必填字段都存在
2. `repo` 字段匹配文件名
3. `anchors` 至少 1 个 PR 号
4. Hard Rejections 至少 1 条 rule
5. 每个 rule 必须含"规则 / 锚点 / 原因 / 正确做法"4 段

缺字段 → error. 缺某段 → warning.

## Agent 调用

```python
from prgenius.triage import triage_pr

# 默认加载 docs/policies/<org>-<repo>.md
result = triage_pr(
    title="fix: typo",
    repo="Ikalus1988/MisakaNet",
    body="Just a typo fix",
    diff_stat="README.md | 3 ++-",
)
# → {verdict: "pass", policy_loaded: True, violations: []}
# OR
# → {verdict: "reject", policy_loaded: True, violations: [{rule_number: 1, evidence: "..."}]}
```
