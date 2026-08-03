# Status MVP Trial — 2026-08-02

## 试运行概况

首次使用 `prgenius status` 替代手动逐个 PR shell 检查。

### 输入
```bash
python3 -m prgenius status --author zsxh1990 --stale-days 14
```

### 输出摘要
```
🔴 NEEDS_REBASE     3  harbor #2121, railtracks #1190, memex #221
🟡 STALE_REVIEW     1  mongodb #1309
🔴 CHANGES_REQUESTED 1  maigret #2902
🟡 STALE_NO_REVIEW  3  mindbook #2, openlumara #38, qdrant #143
🟡 BLOCKED          2  holmesgpt #2305, honcho #801
⏭️ IGNORED          3  OWN_REPO
```

### 与手动心跳对比

| PR | 手动判断 | status 输出 | 一致？ |
|---|---|---|---|
| holmesgpt #2305 | MERGEABLE/BLOCKED | BLOCKED | ✅ |
| maigret #2902 | CHANGES_REQUESTED | CHANGES_REQUESTED | ✅ |
| maigret #2917 | 需要 rebase | **已合并** | ✅ 自动修正 |
| harbor #2121 | 等 review | NEEDS_REBASE | ⚠️ 新发现冲突 |
| memex #221 | 等 review | NEEDS_REBASE | ⚠️ 新发现冲突 |
| railtracks #1190 | 等 review | NEEDS_REBASE | ⚠️ 新发现冲突 |

### 误判分析

| 问题 | 评估 |
|---|---|
| UNKNOWN 是否只是 GitHub 短暂计算？ | 本次运行无 UNKNOWN（上次有 3 个），说明是暂态 |
| BLOCKED 是否过宽？ | holmesgpt #2305 合理（review required），honcho #801 合理（maintainer 未响应） |
| STALE_NO_REVIEW 是否符合实际？ | mindbook 29d、openlumara 19d、qdrant 23d — 均超过 14d 阈值，合理 |
| STALE_REVIEW 是否该 ping？ | mongodb #1309 (26d since fix) — 合理，维护者未 re-review |

### 发现的价值

**3 个 NEEDS_REBASE 被手动心跳漏检**：
- harbor #2121、railtracks #1190、memex #221
- 手动检查时只看 reviewDecision，未检查 mergeable
- status 自动检出并提示行动

### 行动执行

| 行动 | 结果 |
|---|---|
| rebase harbor #2121 | ✅ 冲突已解决，已 force push |
| rebase railtracks #1190 | ✅ 无冲突，已 force push |
| rebase memex #221 | ✅ 冲突已解决，已 force push |

### 结论

- Status MVP 验收通过
- 误判率：0/10 PR（无误判）
- 漏检率：手动 3/10（status 全部检出）
- 耗时 ~3min（可接受，阶段二 P0 优化到 <10s）

### P0 GraphQL 批量查询（✅ 完成）

- 单次 `gh api graphql` 替代 2×N 次 CLI 调用
- 13 PR: ~3min → **5s**
- statusCheckRollup.state 为 CI source-of-truth

### 试运行发现

1. **holmesgpt #2305**：GraphQL 返回 BEHIND（CLI 返回 BLOCKED）→ GraphQL 更准确，BEHIND → NEEDS_REBASE
   - **规则：GraphQL source-of-truth 优先级高于旧 CLI 路径**
2. **harbor #2121**：rebase 后 CI 状态 → FAILURE 则 CI_FAILING，PENDING/EXPECTED 则 BLOCKED

### 下一步

1. 阶段二 P1：repo profile 接入 stale_days_threshold
2. 连续跑 3 天（08-02 ~ 08-04），保存快照

---

## Phase 4 Smoke Test — 2026-08-03

### 单元测试

```
63 passed in 0.08s
```

| 测试类 | 数量 | 覆盖 |
|--------|------|------|
| TestEnrichPrFlags | 9 | abandon/ping/rebase 标记逻辑 |
| TestFormatTransitions | 4 | 告警格式 + 推荐行动 |
| TestFormatStepSummary | 4 | GitHub Step Summary |
| TestFormatStepSummaryAnalyze | 1 | analyze Step Summary |
| TestFormatIssueBody | 2 | Issue body 格式 |
| TestNotifyWebhook | 4 | 飞书/Slack/generic dry-run |
| 原有测试 | 39 | 分类器+transition+writeback |

### 端到端 Smoke

| 命令 | 结果 |
|------|------|
| `status --author zsxh1990 --format json` | ✅ 10 PRs, flags 正确 |
| `auto-ping --author zsxh1990` | ✅ 2 pingable PRs |
| `auto-rebase --author zsxh1990` | ✅ 1 rebaseable PR |
| `status --webhook ... --webhook-dry-run` | ✅ payload 正确 |
| `update-issue --dry-run` | ✅ issue body 正确 |

### Phase 4 实时数据

- ping_suggested: 2 (mongodb#1309 STALE_REVIEW 27d, openlumara#38 STALE_NO_REVIEW 20d)
- rebase_suggested: 1 (holmesgpt#2305 BEHIND)
- abandon_candidate: 0 (无超阈值)
