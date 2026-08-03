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

所有 Phase 0-4 功能已实现 ✅

| Phase | 功能 | 状态 |
|-------|------|------|
| 0 | Status MVP, GraphQL, Profile, Transitions | ✅ |
| 1 | 稳定运营（snapshot, 误判记录） | 🔄 持续观察 |
| 2 | transition 告警 + 推荐行动 | ✅ |
| 3 | Step Summary, Labels, 评论, Webhook, Issue | ✅ |
| 4 | auto-ping, auto-rebase, abandon_candidate | ✅ |
