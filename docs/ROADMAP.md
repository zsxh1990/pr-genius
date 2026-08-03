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

## Phase 2 📋 历史追踪增强

| # | 待办 | 说明 |
|---|------|------|
| 4 | transition 告警输出增强 | 用户可见的格式化告警（非纯 JSON） |

## Phase 3 📋 通知与 Bot

| # | 待办 | 说明 |
|---|------|------|
| 5 | GitHub Step Summary | `analyze` 结果写入 `$GITHUB_STEP_SUMMARY` |
| 6 | PR labels 打标 | `pr-genius:low-risk / medium-risk / high-risk` |
| 7 | high_risk 评论提醒 | Action 中仅 high_risk PR 自动留评论 |
| 8 | webhook / 飞书 / Slack | 状态变化推送 |
| 9 | 固定 issue 心跳更新 | pinned issue 展示 outbound PR 状态 |

## Phase 4 📋 Agent 化

| # | 待办 | 说明 |
|---|------|------|
| 10 | auto-ping --dry-run | 默认关闭，respect `max_pings` |
| 11 | auto-rebase --confirm | 默认关闭 |
| 12 | abandon_candidate 标记 | 只建议，不自动 close |

## 当前实现优先级（从易到难）

1. **#5 Step Summary** — 写文件，零依赖
2. **#6 PR labels** — `gh pr edit --add-label`
3. **#7 high_risk 评论** — `gh pr comment`
4. **#4 transition 告警格式** — 格式化输出
5. **#8 webhook 通知** — HTTP POST
6. **#10 auto-ping dry-run** — 读 profile + gh api
7. **#11 auto-rebase** — git operations
8. **#12 abandon_candidate** — 阈值判断 + 建议
