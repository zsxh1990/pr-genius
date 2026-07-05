---
type: PR Case Study
title: mongodb-mcp-server PR #1309 - docs(azure): remove stale tested image version
description: zsxh1990 第一次 mongodb-js 仓 PR，删 Azure deploy README 中的过期版本号
pr_number: 1309
pr_url: https://github.com/mongodb-js/mongodb-mcp-server/pull/1309
repo: mongodb-js/mongodb-mcp-server
author: zsxh1990
status: open
opened_at: 2026-07-02
last_activity: 2026-07-02
tags:
  - pr-case-study
  - docs
  - ponytail-single-source-of-truth
  - xs-pr
  - mongojs-mcp
related:
  - ../index.md
verified_at: "2026-07-05T01:08:34Z"
evidence_urls:
  - https://github.com/mongodb-js/mongodb-mcp-server/pull/1309
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309/files
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/issues/1309/comments
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309/reviews
  - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309/commits
confidence: high
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+1 / -1 / 1 file (deploy/azure/README.md)"
      verified_at: "2026-07-02T16:14:18Z"
      evidence_urls:
        - https://github.com/mongodb-js/mongodb-mcp-server/pull/1309/files
        - https://github.com/mongodb-js/mongodb-mcp-server/pull/1309
        - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309/commits
      confidence: high  # PR created_at from GH API; commits at a02fc16b
      verified_at: "2026-07-02T16:14:18Z"
      evidence_urls:
        - https://github.com/mongodb-js/mongodb-mcp-server/pull/1309/files
        - https://github.com/mongodb-js/mongodb-mcp-server/pull/1309
        - https://api.github.com/repos/mongodb-js/mongodb-mcp-server/pulls/1309/commits
      confidence: high  # PR created_at from GH API; commits at a02fc16b
    response_time_h: null  # 等待 maintainer
    maintainer_action: null
    bot_review: []
    blocker: null
    resolution: null
    timestamp: "2026-07-02T16:13:00Z"
close_decision:
  status: pending
  reason: "第一次 mongodb-js 仓 PR + XS docs 类，等待 maintainer 反应 baseline"
  decided_at: null
  actor: zsxh1990
final_status: open
opened_at: "2026-07-02T16:13:00Z"
last_activity: "2026-07-02T16:13:00Z"
file_change:
  files_changed: 1
  net_diff_chars: -67  # 旧 243 → 新 176
  ponytail_principle: "single-source-of-truth (bicep 当 SSOT, README 不复述)"
source_pr: mongodb-js/mongodb-mcp-server#1309
schema_version: rounds-v0.2.0
---

# mongodb-mcp-server PR #1309: docs(azure): remove stale tested image version

> zsxh1990 在 [mongodb-js/mongodb-mcp-server#1309](https://github.com/mongodb-js/mongodb-mcp-server/pull/1309) 的 docs 探路 PR。  
> **状态**：🟢 open（刚开，等待 maintainer 回应 baseline）  
> **价值**：Ponytail "single-source-of-truth" 守则的实证 + mongodb-js 仓接受度评估入口

---

## PR 内容

**问题**：`deploy/azure/README.md` L11 写过时版本号 "This bicep is tested with version 1.10.0"，但：
- `bicep/main.bicep` 默认 `containerImage = 'mongodb/mongodb-mcp-server:1.13.0'`
- `package.json` 当前 = `1.14.0-prerelease.1`
- 1.10.0 既非 bicep 默认，也非开发版 → **README 完全 stale**

**方案**：删整个 "This bicep is tested with version 1.10.0." 句，让 bicep/main.bicep 当 SSOT（single source of truth）。README 保留大意指向 parameter files。

**规模**：+1 / -1 / 1 file（**67 chars 减少**）

### Diff

```diff
-- MongoDB MCP server container image available in dockerhub registry (mongodb/mongodb-mcp-server:1.10.0). This bicep is tested with version 1.10.0. Please change the parameter files to use other versions of the MongoDB MCP server docker image.
+- MongoDB MCP server container image available in dockerhub registry. Use the parameter files (`bicep/params.json` or `bicep/paramsWithAuthEnabled.json`) to select the version.
```

---

## 关键决策（**Ponytail 守则实证**）

### 决策 B vs A（克莱恩拍板 B）

| 选项 | diff | 问题 |
|---|---|---|
| **A: 改 1.10.0 → 1.13.0** | 1 line | 数字又会 stale，下次还要修 |
| **B: 删整句，让 bicep 当 SSOT** ✅ | 1 line | README 不复述版本号，bicep 是权威 |

**克莱恩的 ponytail 逻辑**："不要把 1.10.0 改成 1.13.0，否则下次又过期。"

### 单源原则在 docs 上下文

- Ponytail 守则核心："stdlib 有 → 用 / 不复述已有信息"
- 扩展：**"config 有 → 用 / docs 不复述 config 值"**
- bicep/main.bicep 是 version 的 SSOT → README 不该再复述具体版本号

---

## 时间线

| 时间 | 事件 |
|---|---|
| 2026-07-02 23:50 GMT+8 | 克莱恩拍板 mongodb-js 探路 |
| 2026-07-03 00:13 GMT+8 | PR #1309 开（fork → upstream） |
| (等待 maintainer 回应) | — |

---

## 验证（克莱恩 5 个 gate 全过）

| Gate | 实际 | 结果 |
|---|---|---|
| ≤ 3 files changed | **1 file** | ✅ |
| ≤ 30 lines diff | **1 line** | ✅ |
| 不需要 MongoDB | **纯 docs** | ✅ |
| 不需要账号/Atlas | **不需要** | ✅ |
| 验证靠 npm test/lint 或 docs 检查 | **docs-only + 不动 .ts/.bicep** | ✅ |
| PR title: fix/docs/chore | **`docs(azure): remove stale tested image version`** | ✅ |

---

## 不撞 6 个禁区

| 禁区 | 命中？ |
|---|---|
| feature | ❌ 纯 docs |
| MCP protocol behavior | ❌ |
| auth/security | ❌ |
| MongoDB connection semantics | ❌ |
| dependency upgrade | ❌（不动 package.json）|
| large refactor | ❌ |

---

## 下一步

- ⏸ 等 maintainer 回应 baseline（mongodb-js 团队节奏 vs 其他友好仓）
- 📊 mongodb-js merge rate: 待 PR #1309 验证是否真的开门型友好
- 🆕 如果合并 → 学到的 baseline 可定 Pr-genius "external PR 友好度档案"
- 🚫 如果 close → 学到的 baseline 可反思"误判 mongodb-js"教训

---

## 关联文档

- [mongodb-js-mongodb-mcp-server 仓 Profile](../index.md)
- [OKF bundle 根入口](../../index.md)
- [BLACKLIST](../../BLACKLIST.md) — mongodb-js 不在拉黑清单
- [anti-patterns](../../anti-patterns/) — 无命中
- [MEMORY.md pr-genius v0.5.0](../../../MEMORY.md#-pr-genius-zsxh1990-仓-v050-沉淀2026-07-02-2356-gmt8)