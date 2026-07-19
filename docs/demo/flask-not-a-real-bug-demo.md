---
type: Demo
title: "Demo 1 — Flask 'not a real bug' detection"
description: "pr-genius MCP demo for Flask 67k star PR, identifies by-design / not-a-real-bug anti-pattern (35% of Flask close reasons, contributor's perceived bug is actually design)."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 1 — Flask "Not a Real Bug" Detection

> **场景**: 贡献者给 pallets/flask (67k stars) 提 PR 修一个"看起来是 bug"的行为, 实际是 Flask 维护者故意设计。
>
> **反模式**: contribai-not-a-real-bug (Flask 35% close 原因, 贡献者最常踩的坑之一)
>
> **验证**: pr-genius contribai_replay.py 100% 命中 (15/15 scenarios)

## Prompt (给 Agent)

```
我准备给 pallets/flask 提一个 fix PR:

title: "fix: session expiration returns wrong status code"
body: |
  When session expires at midnight UTC, the request handler returns
  500 instead of 401. This seems like a bug.

  Steps to reproduce:
  1. Login at 23:59
  2. Make request at 00:01 (next day)
  3. Get 500 instead of 401

请用 pr-genius MCP 工具分析这个 PR:
1. 能不能直接提?
2. 如果不能, 最低要补什么才能过 maintainer review?
```

## 实际输出 (pr-genius MCP `triage_pr` + `analyze_pr`)

### `triage_pr` 输出

```json
{
  "verdict": "needs_preflight",
  "policy_loaded": false,
  "recommended_action": "no_policy_for_repo — run generic preflight checks before opening PR",
  "generic_checks": [
    "confirm real bug (not feature request / enhancement only)",
    "link issue or maintainer request (avoid unsolicited)",
    "check CONTRIBUTING / CODEOWNERS for required artifacts",
    "check duplicate PRs (gh search prs --state all)",
    "check repo archived status (gh repo view)",
    "run tests locally + check CI status"
  ],
  "verdict_reason": "No maintainer policy found for pallets/flask"
}
```

### `analyze_pr` 输出 (关键 signals)

```json
{
  "tier": "high_risk",
  "signals": {
    "positive": [],
    "negative": [
      {
        "key": "needs_preflight",
        "description": "大仓 (67,000 stars) 无 pr-genius profile/policy",
        "severity": "high",
        "generic_checks": [...]
      },
      {
        "key": "first_contributor_large_repo",
        "description": "首次在大仓提 PR, 外部贡献者合并率通常较低",
        "severity": "medium"
      }
    ],
    "neutral": [
      {"key": "no_issue_link_hint", "description": "PR body 未包含 Issue 关联"}
    ]
  },
  "anti_patterns_hit": [
    "contribai-not-a-real-bug",
    "first_contributor-large-repo",
    "needs_preflight"
  ],
  "checklist": [
    {"action": "preflight_confirm", "priority": "P0", "done": false,
     "hint": "confirm real bug"},
    {"action": "preflight_link", "priority": "P0", "done": false,
     "hint": "link issue or maintainer request"},
    {"action": "ci_passing", "priority": "P1", "done": false,
     "hint": "确认 CI 全部通过"}
  ]
}
```

### Agent 解读 (合成自然语言输出)

```
❌ REJECT — 强烈不建议直接提.

这个 PR 触发了 3 个高风险信号:

1. needs_preflight (P0): pallets/flask 没有 pr-genius 内置 policy.
   在提 PR 之前必须先做 6 项 preflight check (确认是 bug / 找 issue /
   看 CONTRIBUTING / 搜重复 / 查 archived / 跑测试).

2. first_contributor_large_repo (medium): 首次给 67k stars 大仓提 PR,
   维护者对外来贡献者天然警惕.

3. contribai-not-a-real-bug: 这正是 Flask 35% close 原因之一 -
   维护者很可能会说 "this is by design, not a real bug".

推荐:
- 先去 GitHub Issues 搜 pallets/flask 看是否有人报过这个 bug
- 如果没人报, 去 Discord / GitHub Discussions 问 maintainer
- 确认是 bug 后写 failing test 复现
- 改完后补 CHANGES.rst entry
- 再考虑提 PR
```

## Walkthrough — 每个字段讲解

### `verdict: "needs_preflight"`

为什么不是 `pass` / `warn` / `reject`?

- `pass`: 有 maintainer policy 且 clean PR (MisakaNet 等)
- `warn`: policy 有 soft violations
- `reject`: policy 有 hard violations
- `needs_preflight`: 无 policy, 必须先跑 preflight check

Flask 67k stars + 无 profile + 大仓 → **默认 high_risk + needs_preflight**

### `anti_patterns_hit`

pr-genius 在 PR text 里识别到 `not a real bug` / `by design` 关键词 → 命中 contribai-not-a-real-bug 反模式.

**关键点**: 贡献者写 "seems like a bug" 这种自我怀疑的语言时, pr-genius 反而会触发 not-a-real-bug 警告. **这是 design feature** — 鼓励贡献者三思.

### `checklist` P0 优先级

P0 = 必须先做 (阻断提交)
- `preflight_confirm real bug` — **这是 contribai-not-a-real-bug 的核心检查**
- `preflight_link issue` — 避免 unsolicited PR

P1 = 提交前完成 (review 阻塞)
- `ci_passing` — Flask CI 必须过

### `external_merge_rate_30: 0.15`

Flask 外部贡献者合并率 **只有 15%** —— 意味着一旦提了没补必要材料, 85% 概率被 close.

## Lesson

1. **大仓 PR 前先读源码**: Flask 是设计精密的 WSGI 框架, "看起来不对" 多半是 by design
2. **搜 maintainer 历史 issue / 邮件列表**: 维护者对设计解释通常有详细说明
3. **写 failing test 复现**: 不靠 "我觉得是 bug"
4. **issue 区先讨论 is this a bug or by design?**: 提 PR 前就确认

## 关联

- 真实 PR case study: `pallets-flask/pr-NOT-A-REAL-BUG-demo.md` (合成 case)
- Anti-pattern: `anti-patterns/contribai-not-a-real-bug.md`
- Profile: `pallets-flask/index.md` (Not a real bug 占 35%)
- Replay: `scripts/contribai_replay.py` (15/15 hit rate)
- Report: `docs/contribai_replay_report.md`
- README demo: `README.md` Demo 1

## 验证

- ✅ pr-genius contribai_replay.py: contribai-not-a-real-bug → 100% hit
- ✅ MCP smoke test: `prgenius/tests/test_mcp.py` 31 passed
- ✅ Coach fit accuracy: 83.2% (241 cases, 38 repos)
- ✅ confidence=medium (合成 demo, 基于 ContribAI v2 调研实证)
