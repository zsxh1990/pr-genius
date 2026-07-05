---
type: Repo Profile
title: agentic-community/mcp-gateway-registry PR 模式分析
description: Enterprise MCP Gateway & Registry 仓 — zsxh1990 PR #1382 + #1383 docs/mermaid-render typo fix 双发经验
repo: agentic-community/mcp-gateway-registry
url: https://github.com/agentic-community/mcp-gateway-registry
star: 765
fork: 201
language: Python
size_kb: 57295
default_branch: main
zsxh_pr_count: 2
status: in-flight
data_source: zsxh PR #1382 (auth.md) + #1383 (egress-credential-vault.md)
analyzed_at: 2026-07-04
tags:
  - repo-profile
  - mcp
  - gateway
  - registry
  - oauth2
  - keycloak
  - mongodb
  - documentdb
  - aws
  - python
related:
  - ./pr-1382-auth-md-mermaid-token.md
  - ./pr-1383-egress-vault-mermaid-placeholders.md
agent_guidelines:
  allow_unsolicited_pr: true
  require_signed_off: false
  require_cla: false
  require_changeset: false
  require_issue_first: false
  ai_policy: welcoming  # 无反 AI 信号，主动 merge docs typo fix 类小 PR
  ai_assisted_disclosure: false  # 未在 CONTRIBUTING 强制要求
  human_required_in: []
  maintainer_vibe: responsive
federates_with:
  - target: MisakaNet (Ikalus1988/MisakaNet)
    mode: query-only
verified_at: "2026-07-05T14:53:11.740158Z"
evidence_urls:
  - https://github.com/agentic-community/mcp-gateway-registry
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/releases/latest
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/commits
confidence: high  # autogen from GH API; bump to medium if human-curated
last_release: 1.25.0
last_commit_sha: 1d2f5d46
stars: 766
---


# agentic-community/mcp-gateway-registry

## 仓画像

| 维度 | 值 |
|---|---|
| Star | 765 ★ |
| Fork | 201 |
| Language | Python |
| Size | 57MB |
| Open issues | 94 |
| Topics | mcp, mcp-gateway, mcp-registry, oauth2, mongodb, agentic-ai, a2a, terraform, ecs-fargate |
| Default branch | main |
| License | (need check — profile-only mode) |
| Maintainer org | agentic-community (community org, 多个 maintainer) |
| Pushed | 持续 pushed（7/4 03:07 GMT = 维护者凌晨活跃）|

## 维护者风格

- 节奏：**🚀 频繁 merge** —— 7/3-7/4 单日合并 9+ PR
- 关注点：安全清理（SA-X 编号 fix）+ docs 修（mermaid render）+ 配置调整（`reuse uv.lock` 类）
- 习惯：**no-issue-ref needed** —— 多个 PR (#1373, #1375, #1381 等) 直接 merge 不引用具体 issue
- 守卫：`/scripts/codestyle-and-validation.yml` + `Build Documentation` GitHub Action（per-PR）
- 反 AI：**没看到**明显敌视。CONTRIBUTING.md 提到 AI-assisted（待确认）

## PR 友好度矩阵

| 类型 | 友好度 | 历史样本 |
|---|---|---|
| docs typo/mermaid fix | 🟢 高 | PR #1373 (mermaid syntax), #1375 (sequenceDiagram quoted), #1320 (configurable timeout), #1356 (configurable timeout follow-up) |
| security fix (SA-X) | 🟢 高 | 7/3-7/4 一周合并 #1374 + #1376 + #1380 + #1381 等 4 个 |
| linter skip placement | 🟢 高 | #1372 checkov skip placement |
| config 修正 | 🟢 高 | #1371 reuse uv.lock for precommit tests |
| enhancement / feat | 🟡 中 | #1322 (Grafana dashboard) 走完流程但 fix 类型 ~enhancement |
| large refactor | 🟡 中 | 历史经验 |
| breaking | ⚠️ 红线 | #3023 `feat!:` promote autogen.beta → 维护者自家接受 |

## 已知反模式

- **大 deployment 文件 drift** (7/4 #1377/#1378/#1379 三连同一人 Mathewcraig1 7小时发，c=0 等待) —— `docker-compose.podman.yml` 默认值与 docs 不一致
- **env var naming 不一致** (KEYCLOAK_EXTERNAL_URL/MCP_HTTPS_REQUIRED) —— 维护者用了大量两个不同的 env prefix
- **schema 频繁变** —— 6/27 才 `feat!:` promoted autogen.beta → autogen，文档落后

## 提 PR 友好方向（按 ROI 排）

1. **🥇 docs mermaid render 修复** —— 跟维护者节奏完全 match；model-on build action `Build Documentation` 直接验证
2. **🥈 config / default value 漂移修复** —— `#1377-#1379` 类 issue 直击；单 file 多修改但每行 ≤ 5 file 很常见
3. **🥉 CI / checkov 单行 fix** —— #1372 类
4. **🟡 内部 dependency single-line patch** —— uv.lock 调整类（注意：MEMORY 警告 —— uv lock 修改有 PR 风险）

## 风险区

- **不要碰 multi-service deployment 改动**（terraform / keycloak + documentdb + ecs 全栈）—— 即使小改动也撞依赖 lockfile
- **不要碰 oauth/identity 中间件**—— #1265/#1266/#1268/#1269 是维护者自家在做
- **不要碰 `prometheus` / `metrics` / observability 改造**—— #2762+#1101 等大坑

## 太阳在这仓的实测

2 个 PR：
- **#1382** `[docs]` `<token>` → `[token]` mermaid fix (1 file, 1 line) — 7/4 GMT+8 04:05 open
- **#1383** `[docs]` `<server>` + `<path>` mermaid fix (1 file, 2 lines) — 7/4 GMT+8 04:07 open

→ 详见 [pr-1382-auth-md-mermaid-token.md](./pr-1382-auth-md-mermaid-token.md) +
   [pr-1383-egress-vault-mermaid-placeholders.md](./pr-1383-egress-vault-mermaid-placeholders.md)

## 数据源

- GitHub API 抓 repo + PRs（2026-07-04）
- `git clone --depth 20` 本地验证 mermaid blocks
- 7/3-7/4 维护者合并的 ~10 PR 做样本
