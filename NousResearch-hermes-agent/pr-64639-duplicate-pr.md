---
type: PR Case Study
title: "duplicate PR — NousResearch #64639 (zsxh1990 scout-phase 命中记录)"
description: "NousResearch/hermes-agent #64639 — 第三方 PR 标记 duplicate。反模式：未搜索已有 PR / 未检查 main 分支 / Issue 已被人修。fix_action: 提 PR 前必查 search + main HEAD + Issue 区。"
repo: NousResearch/hermes-agent
pr_number: 64639
pr_url: https://github.com/NousResearch/hermes-agent/pull/64639
author: third-party
final_status: closed-not-merged
opened_at: "2026-07-15T00:00:00Z"
closed_at: null
verified_at: "2026-07-19T14:48:00Z"
evidence_urls:
  - https://github.com/NousResearch/hermes-agent/pull/64639
  - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-duplicate-pr.md
confidence: medium
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - nousresearch
  - duplicate-pr
  - anti-pattern
  - scout-phase
rounds:
  - round: 1
    action: open
    delta:
      kind: unknown
      value: null
      verified_at: "2026-07-15T00:00:00Z"
      evidence_urls:
        - https://github.com/NousResearch/hermes-agent/pull/64639
      confidence: low
    response_time_h: null
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: label duplicate"]
    blocker: "duplicate of existing PR (search 必查项失败)"
    resolution: null
    commit: null
    timestamp: "2026-07-15T00:00:00Z"
  - round: 2
    action: bot_review
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-07-15T01:00:00Z"
      evidence_urls:
        - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-duplicate-pr.md
      confidence: medium
    response_time_h: 1
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: duplicate marker set"]
    blocker: null
    resolution: "PR 进入 sweeper-closing 队列"
    commit: null
    timestamp: "2026-07-15T01:00:00Z"
close_decision:
  status: pending
  reason: "sweeper 标记 duplicate, 等待 maintainer 或 author 自决"
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
    - "duplicate"
    - "implemented-on-main"
    - "sweeper:implemented-on-main"
  - one_pr_friendly: true
links:
  - type: anti-pattern
    target: anti-patterns/nousresearch-duplicate-pr.md
    note: "直接对应 duplicate-pr anti-pattern key"
  - type: research
    target: ../../hermes-agent-pr-knowledge/report.md
---

# PR #64639 — duplicate PR

## 摘要

NousResearch/hermes-agent #64639 — 第三方贡献者提的 PR 被 hermes-sweeper[bot] 标记 `duplicate`。**典型 duplicate 反模式样本**：未搜索已有 PR / 未检查 main 分支最新代码 / Issue 区已有人修复。

## 反模式来源

`research/big-repo-pr-knowledge/anti-patterns/nousresearch-duplicate-pr.md`（key: `nousresearch-duplicate-pr`，severity: medium）

## 时间线

| 日期 | 事件 |
|---|---|
| 2026-07-15 00:00 | 第三方提 PR |
| 2026-07-15 01:00 | hermes-sweeper[bot] 标记 duplicate |
| 2026-07-15+ | sweeper-closing 队列 |

## 学到的规则（from anti-pattern）

1. **提 PR 前必查**：
   - `gh search prs --repo NousResearch/hermes-agent --state all "<keyword>"` —— 搜已有 PR
   - `gh search issues --repo NousResearch/hermes-agent --state all "<keyword>"` —— 搜 Issue
   - `git fetch origin main && git log origin/main` —— 看 main 是不是已修
2. **置信度判断**：
   - 如果搜到状态 open 已有同类 PR → 不重复提，先参与讨论
   - 如果搜到状态 closed merged → 引用已有 commit，不重新提
   - 如果 Issue 区有人说"我打算做" → 等或协作
3. **fix_action**（来自 anti-pattern key）：
   - 1) 搜索已有 PR 和 Issue
   - 2) 检查 main 分支最新代码
   - 3) 确认问题是否已解决

## zsxh1990 应用价值

NousResearch-hermes-agent 处于 **scout-phase**（克莱恩 7/3 拍板，zsxh_pr_count=0）。这种仓**首次提 PR = 信用投资**，duplicate 失败 = 信用负分。

**实操 checklist**（提 PR 前必跑）：
```bash
# 1. 关键词搜已有 PR
gh search prs --repo NousResearch/hermes-agent --state all "<keyword>"

# 2. 搜相关 Issue
gh search issues --repo NousResearch/hermes-agent --state all "<keyword>"

# 3. 看 main 是不是已修
git fetch origin main
git log --oneline origin/main | head -20

# 4. 检查 sweeper 历史 tag 模式（看哪些 close reason 最常见）
gh pr list --repo NousResearch/hermes-agent --state closed --limit 100 \
  --json number,title,labels | jq '.[] | .labels[].name' | sort | uniq -c
```

## 关联

- 反模式：`research/big-repo-pr-knowledge/anti-patterns/nousresearch-duplicate-pr.md`
- 同类 PR：#53124 (sweeper:implemented-on-main)
- 调研报告：`hermes-agent-pr-knowledge/report.md`

## 验证

- ⚠️ confidence=medium（无 deep_read 原文，从 anti-pattern source_pr 字段反推）
- ✅ 真实 PR URL 锚点
- ✅ rounds + close_decision
- ✅ agent_guidelines_applied
- ✅ 实操 checklist
