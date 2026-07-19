---
type: PR Case Study
title: "comp/cron 定时任务风险 — NousResearch #42920"
description: "NousResearch/hermes-agent #42920 — 第三方 PR 触发 comp/cron 标签。反模式：定时任务改动未测试边界情况（时区 / 夏令时 / 服务重启）。fix_action: 时区测试 + DST 边界测试 + 重启场景 + 回滚方案。"
repo: NousResearch/hermes-agent
pr_number: 42920
pr_url: https://github.com/NousResearch/hermes-agent/pull/42920
author: third-party
final_status: closed-not-merged
opened_at: "2026-XX-XX"
closed_at: null
verified_at: "2026-07-19T14:52:00Z"
evidence_urls:
  - https://github.com/NousResearch/hermes-agent/pull/42920
  - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-cron-risk.md
confidence: medium
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - nousresearch
  - comp-cron
  - timezone
  - dst
  - scheduled-task
  - anti-pattern
  - scout-phase
rounds:
  - round: 1
    action: open
    delta:
      kind: unknown
      value: null
      verified_at: "2026-XX-XX"
      evidence_urls:
        - https://github.com/NousResearch/hermes-agent/pull/42920
      confidence: low
    response_time_h: null
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: comp/cron 标签触发"]
    blocker: "定时任务调度 / 执行 / 错误处理逻辑修改，未测时区 / DST / 重启"
    resolution: null
    commit: null
    timestamp: "2026-XX-XX"
  - round: 2
    action: bot_review
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-XX-XX+24h"
      evidence_urls:
        - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-cron-risk.md
      confidence: medium
    response_time_h: 24
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: 需要时区测试 + DST 边界 + 回滚方案"]
    blocker: "fix_action: 1) 测试定时任务可靠性 2) 边界情况 3) 回滚方案"
    resolution: "等待 author 补测试或 close"
    commit: null
    timestamp: "2026-XX-XX+24h"
close_decision:
  status: pending
  reason: "定时任务改动需要时区 / DST / 重启场景覆盖测试, sweeper 提示后等待 author 动作"
  decided_at: null
  actor: hermes-sweeper[bot]
agent_guidelines_applied:
  - allow_unsolicited_pr: true
  - require_signed_off: false
  - require_cla: false
  - require_changeset: false
  - require_issue_first: false
  - ai_policy: welcoming
  - ai_assisted_disclosure: false
  - maintainer_vibe: selective-responsive
  - bot_review: heavy
  - ci_first_run_needs_approval: false
  - default_branch: main
  - response_time_h_median: 72
  - external_merge_rate_30: 0.473
  - close_keywords:
    - "comp/cron"
    - "scheduled task"
    - "timezone"
    - "DST"
  - one_pr_friendly: true
links:
  - type: anti-pattern
    target: anti-patterns/nousresearch-cron-risk.md
  - type: contrast
    target: NousResearch-hermes-agent/pr-64639-duplicate-pr.md
    note: "duplicate = 快速 close; cron = 等待 author 补测试. 两种 sweeper close 模式."
  - type: contrast
    target: NousResearch-hermes-agent/pr-52917-comp-desktop-platform-windows.md
    note: "desktop = 跨平台测试; cron = 时区/DST/重启测试. 两者都是 '未测边界情况' 反模式"
  - type: research
    target: ../../hermes-agent-pr-knowledge/report.md
---

# PR #42920 — comp/cron 定时任务风险

## 摘要

NousResearch/hermes-agent #42920 — 第三方 PR 触发 `comp/cron` 标签。**典型定时任务反模式样本**：修改定时任务调度 / 执行 / 错误处理逻辑，但未测时区、夏令时、服务重启等边界情况。

## 反模式来源

`research/big-repo-pr-knowledge/anti-patterns/nousresearch-cron-risk.md`（key: `nousresearch-cron-risk`，severity: medium）

## 学到的规则

### 定时任务 PR 必做 3 件事

#### 1. 时区测试

```python
# 测试跨时区行为
def test_cron_fires_in_user_timezone():
    user_tz = pytz.timezone("America/New_York")
    user_now = datetime.now(user_tz)
    # cron 表达式应基于 user TZ, 不是 UTC
```

常见错误：
- 用 `datetime.utcnow()` 而非 `datetime.now(tz=...)`
- 假设 server 在 UTC，user 在其他 TZ
- DST 切换日（春进 / 秋退）行为不一致

#### 2. DST 边界测试

```python
# 2026-03-08 02:00 美国切换到 DST (春进)
# 2026-11-01 02:00 美国切回标准时间 (秋退)
def test_cron_handles_dst_spring_forward():
    # 02:00-03:00 不存在, 应该 skip 或 fire at 03:00
    pass

def test_cron_handles_dst_fall_back():
    # 02:00 触发两次, 应该去重
    pass
```

#### 3. 重启场景 + 回滚方案

```python
def test_cron_survives_restart():
    # 服务在 cron 触发时刻重启
    # 任务应: 跳过本次 / 立即触发 / 下次触发, 取决于语义
    pass

def test_cron_rollback_on_failure():
    # 任务执行失败 → 是否回滚已修改的数据?
    pass
```

## 触发条件（反模式 key）

1. 修改定时任务调度逻辑（cron 表达式 / 触发频率 / 触发时间）
2. 修改定时任务执行逻辑（任务内容 / 执行顺序 / 资源使用）
3. 修改定时任务错误处理（retry / dead-letter / alerting）

## zsxh1990 应用价值

NousResearch scout-phase。**首次 PR 避免碰 cron**（除非有完整时区 + DST + 重启测试 setup）。

如果必须做 cron PR，模板：
```markdown
## Cron / Scheduled Task Considerations

### Schedule
- Cron expression: `0 */6 * * *` (every 6 hours)
- User timezone aware: yes (uses `pytz.timezone`)
- DST handling: skip on spring-forward, dedupe on fall-back

### Tested scenarios
- [ ] Cross-timezone (user in UTC+8, server in UTC)
- [ ] DST spring-forward (2026-03-08 02:00 → 03:00)
- [ ] DST fall-back (2026-11-01 02:00 fires twice → dedupe)
- [ ] Service restart during scheduled fire
- [ ] Task failure → rollback / retry / dead-letter

### Rollback plan
- Disable cron via feature flag `HERMES_CRON_ENABLED=false`
- Restore previous schedule from config backup
- Manual cleanup via `hermes-cli cron cleanup --task=...`
```

## 关联

- 反模式：`research/big-repo-pr-knowledge/anti-patterns/nousresearch-cron-risk.md`
- 对比：`NousResearch-hermes-agent/pr-64639-duplicate-pr.md` (快速 close)
- 对比：`NousResearch-hermes-agent/pr-52917-comp-desktop-platform-windows.md` (跨平台测试)
- 调研：`hermes-agent-pr-knowledge/report.md`

## 验证

- ⚠️ confidence=medium（无 deep_read 原文，从 anti-pattern source_pr 字段反推）
- ✅ 真实 PR URL
- ✅ rounds + close_decision
- ✅ agent_guidelines_applied
- ✅ cron PR 模板（时区 + DST + 重启 + 回滚）
