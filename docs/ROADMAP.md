---
type: Documentation
title: PR Genius Roadmap
updated: 2026-08-03
---

# PR Genius Roadmap

> 源文档：[PRD 评审稿](https://mi.feishu.cn/docx/LSDRdqmcTo57m5xkgXAcooqEn3g)

## Phase 0 ✅ 完成

| 功能 | 状态 |
|------|------|
| Status MVP — 9 状态分类 + 优先级 | ✅ |
| GraphQL 批量查询（13 PR ≈ 5s） | ✅ |
| Repo Profile + `stale_days_threshold` | ✅ |
| `--save-snapshot` + transition 侦测 | ✅ |
| `analyze --format json`（Action JSON 契约 v1.3.1） | ✅ |
| `coach` / `harvest` 命令 | ✅ |
| `ignored_reason=OWN_REPO` 过滤 | ✅ |
| Profile writeback（suggest + auto） | ✅ |

## Phase 1 🔄 稳定运营

| # | 待办 | 验收标准 |
|---|------|----------|
| 1 | 连续 7 天 snapshot 保存 | cron 零中断 |
| 2 | 误判/漏判样本记录 | 人工抽查 20 PR，误判率 <5% |
| 3 | MisakaNet tier 稳定性 | 2-3 PR 无 tier=unknown 回归 |

## Phase 2 ✅ 历史追踪增强

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 4 | transition 告警输出增强 | `_TRANSITION_ACTIONS` 推荐行动 + `format_transitions()` | ✅ |

## Phase 3 🔄 通知与 Bot

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 5 | GitHub Step Summary | `format_step_summary()` + `--step-summary` flag | ✅ |
| 6 | PR labels 打标 | Action 中 `pr-genius:low/medium/high-risk` | ✅ |
| 7 | high_risk 评论提醒 | Action 中仅 high_risk PR 自动留非阻塞评论 | ✅ |
| 8 | webhook / 飞书 / Slack | `notify_webhook()` 飞书/Slack/generic + `--webhook` flag | ✅ |
| 9 | 固定 issue 心跳更新 | `update-issue` 命令 + `format_issue_body()` | ✅ |

## Phase 4 🔄 Agent 化

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 10 | auto-ping --dry-run | `auto-ping` 命令，默认 dry-run，`--confirm` 执行 | ✅ |
| 11 | auto-rebase --confirm | `auto-rebase` 命令，默认 dry-run，`--confirm` 调 GitHub API | ✅ |
| 12 | abandon_candidate 标记 | `enrich_pr_flags()` 超阈值标记，只建议不自动 close | ✅ |

## 实现状态

| Phase | 功能 | 状态 |
|-------|------|------|
| 0 | Status MVP, GraphQL, Profile, Transitions | ✅ |
| 1 | 稳定运营（snapshot, 误判记录） | 🔄 持续观察 |
| 2 | transition 告警 + 推荐行动 | ✅ |
| 3 | Step Summary, Labels, 评论, Webhook, Issue | ✅ |
| 4 | auto-ping, auto-rebase, abandon_candidate | ✅ |
| 5 | Maintainer View (5-action routing) | ✅ v1.5.0 |
| 5.1 | Maintainer 增强 (impact/review/author/conflicts) | 📋 v1.5.1 |
| 5.2 | Action 复用性改造 (多仓库支持) | 📋 v1.5.2 |
| 6 | Contributor View | 📋 v1.6.0 |

## Phase 5 ✅ v1.5.0 — Maintainer View

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 13 | maintainer_view 模块 | `maintainer_view.py` (427 行) — 5-action routing | ✅ |
| 14 | review queue digest | `docs/maintainer/pr-review-queue.md` 示例 + checklist | ✅ |
| 15 | MCP 暴露 maintainer tools | `mcp.py` +83 行 | ✅ |
| 16 | maintainer_view 单元测试 | 20 测试，覆盖 5 actions + filters + next_step + e2e mock | ✅ |

**安全边界**（学自 OpenClaw PR #93310 复盘）：
- read-only / advisory-only
- **never auto-close / auto-label / auto-comment / auto-merge**
- `--write-digest` opt-in

## Phase 5.1 🔄 v1.5.1 — Maintainer View 增强（维护者决策辅助字段）

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 21 | `impact` 字段 | files_changed / lines_added / lines_deleted / scope / breaking_change / security_sensitive / dependency_changes | 计划 |
| 22 | `review` 字段 | complexity (low/medium/high) / estimated_minutes / needs_domain_expert | 计划 |
| 23 | `author` 字段 | association / previous_prs / merge_rate / first_time | 计划 |
| 24 | `conflicts` 字段 | has_conflicts / conflicting_prs | 计划 |
| 25 | 更新 Bot 评论格式 | 展示 impact / review / author 字段 | 计划 |
| 26 | 更新 MCP 输出 | maintainer_view 返回新字段 | 计划 |

**数据来源**：
- `impact`: `gh pr diff --stat` + 标题 `!` / `BREAKING CHANGE` + 文件路径匹配
- `review`: 文件数 + 行数启发式
- `author`: GitHub API (`author_association` + 历史 PR 统计)
- `conflicts`: GitHub API (`mergeable` + `merge_commit_sha`)

## Phase 5.2 🔄 v1.5.2 — Action 复用性改造（多仓库支持）

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 27 | Action workflow 参数化 | 去掉 `zsxh1990/pr-genius` 硬编码，用 `${{ env.PR_GENIUS_URL }}` | 计划 |
| 28 | 无画像降级 | 没有 repo profile 时用通用规则（star/merge_rate 默认值） | 计划 |
| 29 | 通用 anti-patterns | 只保留通用反模式，去掉仓库专属的 | 计划 |
| 30 | Policy 模板 | 预置常见 policy 模板（Python/JS/Rust/Go） | 计划 |
| 31 | 复用文档 | `docs/setup/README.md` — 5 分钟接入指南 | 计划 |

**复用架构**：
```
prgenius/
├── core/           # 核心逻辑（可复用）
├── profiles/
│   ├── builtin/    # 预置画像（热门仓库）
│   └── custom/     # 用户自定义
├── anti-patterns/
│   ├── builtin/    # 通用反模式
│   └── custom/     # 仓库专属
└── policies/
    ├── builtin/    # 通用策略
    └── custom/     # 仓库专属
```

## Phase 6 🔄 v1.6.0 — Contributor View (计划中)

| # | 待办 | 说明 | 状态 |
|---|------|------|------|
| 32 | contributor view 模块 | 共享 v1.5.0 tier / signals / impact / review 基础设施 | 计划 |
| 33 | persona-specific 决策层 | action / next_step / review_ready / blocking_signals | 计划 |
| 34 | contributor unit tests | 跟 v1.5.0 测试同覆盖深度 | 计划 |
| 35 | docs/contributor/ 示例 | 跟 v1.5.0 文档同结构 | 计划 |
