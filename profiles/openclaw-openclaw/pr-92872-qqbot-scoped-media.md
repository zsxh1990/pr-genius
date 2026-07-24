---
type: PR Case Study
title: "fix(qqbot): allow scoped sandbox media sends — proof: sufficient 但仍 security-boundary 关闭"
description: "zhangguiping-xydt 提给 OpenClaw 的 QQBot 沙箱媒体路径修复 PR；1012 行 / 12 文件 / proof: sufficient / rating: 🐚 platinum hermit（仅次 🦞 diamond lobster）/ 完整 ClawSweeper + build 证明 → 仍因 merge-risk: security-boundary 关闭。教训：security-boundary 标签的优先级高于 proof + rating。"
repo: openclaw/openclaw
pr_number: 92872
pr_url: https://github.com/openclaw/openclaw/pull/92872
author: zhangguiping-xydt
final_status: closed-not-merged
opened_at: "2026-06-14T05:08:31Z"
closed_at: "2026-06-25T15:10:33Z"
verified_at: "2026-07-19T14:43:00Z"
evidence_urls:
  - https://github.com/openclaw/openclaw/pull/92872
  - https://github.com/openclaw/openclaw/pull/92872/files
  - https://api.github.com/repos/openclaw/openclaw/pulls/92872
  - https://api.github.com/repos/openclaw/openclaw/pulls/92872/commits
  - https://research/openclaw-pr-knowledge/report.md
confidence: high
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - openclaw
  - qqbot
  - sandbox-media
  - platinum-hermit
  - security-boundary
  - proof-sufficient
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+1012 / -82 / 12 files"
      verified_at: "2026-06-14T05:08:31Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/92872/files
      confidence: high
    response_time_h: 0.1
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: needs maintainer review before merge（proof: sufficient）"]
    blocker: null
    resolution: null
    commit: "5e8f1d77c8"
    timestamp: "2026-06-14T05:08:31Z"
  - round: 2
    action: bot_review
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-23T21:29:00Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/92872#issuecomment-4792199821
      confidence: high
    response_time_h: 232
    maintainer_action: null
    bot_review: ["clawsweeper[bot]: 9 天后深度 review, source-level 复现 high-confidence"]
    blocker: "ClawSweeper: mediaAccess propagation across 8 outbound paths verified, no critical issues found"
    resolution: null
    commit: null
    timestamp: "2026-06-23T21:29:00Z"
  - round: 3
    action: close
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-25T15:10:33Z"
      evidence_urls:
        - https://github.com/openclaw/openclaw/pull/92872
      confidence: high
    response_time_h: 42
    maintainer_action: "vincentkoc: close 决定"
    bot_review: null
    blocker: "merge-risk: 🚨 security-boundary（QQBot 媒体路径 = 用户可见 attack surface）"
    resolution: "OpenClaw 团队决定不合并沙箱扩展点的 QQBot 实现，等 plugin/community path"
    commit: null
    timestamp: "2026-06-25T15:10:33Z"
close_decision:
  status: close
  reason: "QQBot 沙箱媒体路径 = 用户可见 attack surface。OpenClaw 团队决定不通过 PR 形式扩展沙箱 → 走 plugin/community path（ClawHub / 第三方 channel adapter）。"
  decided_at: "2026-06-25T15:10:33Z"
  actor: vincentkoc (maintainer)
agent_guidelines_applied:
  - allow_unsolicited_pr: true
  - require_signed_off: false
  - require_cla: false
  - require_issue_first: false
  - ai_policy: welcoming
  - ai_assisted_disclosure: true  # PR body 顶部 AI-assisted badge
  - maintainer_vibe: strict
  - bot_review: clawsweeper
  - ci_first_run_needs_approval: false
  - default_branch: main
  - response_time_h_median: 240
  - merge_rate_30d: 0.27
  - close_keywords:
    - "out of scope"
    - "merge-risk: security-boundary"
    - "plugin scope"
  - one_pr_friendly: false
links:
  - type: contrast
    target: openclaw-openclaw/pr-93310-openclaw-error-handler.md
    note: "同 security-boundary close, 但本 PR 有 proof: sufficient + platinum hermit → 仍 close. 证明 security-boundary 优先级高于 proof + rating"
  - type: anti-pattern
    target: anti-patterns/openclaw-channel-extension-scope-fit.md
  - type: research
    target: research/openclaw-pr-knowledge/report.md
    anchor: "§4.3 security-boundary 标签分析"
---

# PR #92872 — QQBot 沙箱媒体路径

## 摘要

zhangguiping-xydt 提给 OpenClaw 的 QQBot 沙箱媒体路径修复：让 sandbox-enabled agent 在 QQBot 上能发送 workspace 内文件。**1012 行 / 12 文件**、ClawSweeper 给 **proof: sufficient** + **rating: 🐚 platinum hermit**（仅次 🦞 diamond lobster）、9 天后 source-level 复现 high-confidence 无 critical issues。**仍被 maintainer 关闭**，原因：QQBot 媒体路径 = 用户可见 attack surface，OpenClaw 团队决定走 plugin/community path。

## 为什么这例重要

跟 PR #93310 形成对比：
- **#93310**：proof 不足 + shell injection + gold shrimp → close（作者代码问题）
- **#92872**：proof 充足 + 无代码缺陷 + platinum hermit → **仍 close**（security-boundary 不可 amend）

**结论**：OpenClaw 的合并门槛不是"代码质量"而是"产品边界"。security-boundary 标签的优先级高于 proof + rating。

## 时间线

| 日期 | 事件 |
|---|---|
| 2026-06-14 05:08 | 提 PR（v1: +1012/-82/12 files, 15 commits, full proof） |
| 2026-06-14 05:10 | ClawSweeper 首次 review: needs maintainer review（无 critical） |
| 2026-06-23 21:29 | ClawSweeper 深度 re-review: source-level 复现 8 outbound paths, high-confidence 验证通过 |
| 2026-06-25 15:10 | vincentkoc 决定 close：QQBot 媒体路径 = attack surface，等 plugin path |

## PR 内容

### 根因修复

**问题**：sandbox-enabled agent 在 workspace 创建文件后想通过 QQBot 发送 → QQBot outbound 路径**丢弃** core 给的 scoped media access，文件被 QQBot API 拒绝。

**修复**：
- 贯穿 8 个 QQBot outbound 路径（direct send / gateway dispatch / tool media forwarding / official C2C streaming / `<qqmedia>` tags / structured `QQBOT_PAYLOAD` / missing-voice staging / host-read voice staging）
- 保持 core 拥有的 sandbox media-access contract 不变
- host-read voice/audio 走 scoped loader 进 QQBot 媒体存储 → SILK 转码复用

### Proof 质量（platinum hermit 评级证据）

- ✅ 完整 regression test（340 source + 590 tests = 930 行测试）
- ✅ QQBot C2C 真实 runtime 证明（text/media）
- ✅ host-read voice/audio coverage
- ✅ build + `check:test-types` 通过
- ✅ source-level 复现：ClawSweeper 在 PR #92872 9 天后 source 验证 8 outbound paths 无问题

### 为什么仍 close

> The source invariant is that core owns the sandbox media-access contract and each channel must preserve that contract to the low-level media resolver.

QQBot 是 OpenClaw 8 个 channel 之一。OpenClaw 团队政策：**channel-specific 沙箱扩展不走 core PR**，走 plugin/community path（ClawHub / 第三方 channel adapter）。即使代码正确，也撞产品决策。

## 学到的规则

1. **`fix(channel-*)` 大改也撞 security-boundary** — 沙箱相关改动即使 proof 充分，maintainer 仍有最终产品边界否决权
2. **platinum hermit ≠ 必合并** — rating 是 bot 评分门槛，maintainer 决定生死
3. **ClawSweeper 9 天延迟 re-review 不是问题** — bot 评分稳定，但 security-boundary 决定权在 maintainer
4. **attack surface 类改动 = plugin path** — OpenClaw 对"用户可见 attack surface"改动有明确分流政策
5. **15 commits 不是越多越好** — 本 PR 15 commits 是合理的（修复 + 测试拆分），但要避免 #93310 那种 6 amend 后评分降级的情况

## 跟 #93310 的对比

| 维度 | #93310 (zsxh1990) | #92872 (zhangguiping-xydt) |
|---|---|---|
| 行数 | +252/-9/3 | +1012/-82/12 |
| commits | 5（3 amend 后）| 15（initial full） |
| proof | sufficient | sufficient |
| ClawSweeper rating | 🦐 gold shrimp | 🐚 platinum hermit |
| security-boundary | yes | yes |
| 结果 | close（作者主动）| close（maintainer 主动）|
| 关闭原因 | 作者认为不可继续 | maintainer 政策分流 |
| 教训 | shell injection 类反模式 | 产品边界 ≠ 代码质量 |

## 关联

- 反模式：`anti-patterns/openclaw-channel-extension-scope-fit.md`
- 对比：`openclaw-openclaw/pr-93310-openclaw-error-handler.md`
- 研究：`research/openclaw-pr-knowledge/report.md` §4.3

## 验证

- ✅ 真实 GitHub PR URL
- ✅ 3 轮 rounds（v0.5.0 schema）
- ✅ 5 个 evidence_urls
- ✅ close_decision + actor=vincentkoc
- ✅ agent_guidelines_applied
- ✅ 跨案例对比表（#93310 vs #92872）
