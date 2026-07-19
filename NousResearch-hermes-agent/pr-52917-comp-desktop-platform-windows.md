---
type: PR Case Study
title: "comp/desktop + platform/windows 双标签 — NousResearch #52917"
description: "NousResearch/hermes-agent #52917 — 第三方 PR 触发 comp/desktop + comp/platform/windows 双标签。反模式：桌面端 PR 涉及跨平台差异未测透，Windows + macOS + Linux 三方行为不一致风险。"
repo: NousResearch/hermes-agent
pr_number: 52917
pr_url: https://github.com/NousResearch/hermes-agent/pull/52917
author: third-party
final_status: closed-not-merged
opened_at: "2026-06-XX"
closed_at: null
verified_at: "2026-07-19T14:50:00Z"
evidence_urls:
  - https://github.com/NousResearch/hermes-agent/pull/52917
  - https://github.com/NousResearch/hermes-agent/pull/63970
  - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-comp-desktop.md
  - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-risk-platform-windows.md
confidence: medium
schema_version: rounds-v0.5.0
tags:
  - pr-case-study
  - nousresearch
  - comp-desktop
  - platform-windows
  - cross-platform
  - anti-pattern
  - scout-phase
rounds:
  - round: 1
    action: open
    delta:
      kind: unknown
      value: null
      verified_at: "2026-06-XX"
      evidence_urls:
        - https://github.com/NousResearch/hermes-agent/pull/52917
      confidence: low
    response_time_h: null
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: comp/desktop + comp/platform/windows 双标签"]
    blocker: "桌面端跨平台差异（Windows/macOS/Linux 行为不一致）"
    resolution: null
    commit: null
    timestamp: "2026-06-XX"
  - round: 2
    action: bot_review
    delta:
      kind: no_code_change
      value: null
      verified_at: "2026-06-XX"
      evidence_urls:
        - https://research/big-repo-pr-knowledge/anti-patterns/nousresearch-comp-desktop.md
      confidence: medium
    response_time_h: 24
    maintainer_action: null
    bot_review: ["hermes-sweeper[bot]: 需要桌面端特定测试 + 跨平台差异说明"]
    blocker: "fix_action: 1) 测试桌面端兼容性 2) 提供桌面端特定测试 3) 考虑跨平台差异"
    resolution: "等待 author 补测试 / 自觉 close"
    commit: null
    timestamp: "2026-06-XX"
close_decision:
  status: pending
  reason: "桌面端 PR 风险高（跨平台差异未测透），sweeper 双标签提示后等待 author 动作"
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
    - "comp/desktop"
    - "comp/platform/windows"
    - "cross-platform"
    - "desktop-only"
  - one_pr_friendly: false  # 跨平台 PR 不友好（multi-platform 测试要求高）
links:
  - type: anti-pattern
    target: anti-patterns/nousresearch-comp-desktop.md
  - type: anti-pattern
    target: anti-patterns/nousresearch-risk-platform-windows.md
    note: "本 PR 同时触发 2 个 anti-pattern"
  - type: contrast
    target: NousResearch-hermes-agent/pr-64639-duplicate-pr.md
    note: "本例 close 延迟更长（sweeper 等待 author 补测试）, 跟 #64639 快速 close 不同"
  - type: research
    target: ../../hermes-agent-pr-knowledge/report.md
---

# PR #52917 — comp/desktop + platform/windows 双标签

## 摘要

NousResearch/hermes-agent #52917 — 第三方 PR 同时触发 `comp/desktop` + `comp/platform/windows` 两个标签。**典型跨平台 PR 风险样本**：涉及桌面端 UI / 功能 / 配置，未提供桌面端特定测试，跨平台差异（Windows/macOS/Linux）未在 PR body 解释。

## 关联反模式

| Anti-pattern key | 触发条件 | fix_action |
|---|---|---|
| `nousresearch-comp-desktop` | 修改桌面端 UI / 功能 / 配置 | 测试桌面端兼容性 + 桌面端特定测试 + 跨平台差异 |
| `nousresearch-risk-platform-windows` | 涉及 Windows 特定行为 | 解释 Windows vs Unix 路径 / shell / 权限差异 |

## 时间线

| 日期 | 事件 |
|---|---|
| 2026-06-XX | 第三方提 PR |
| 2026-06-XX +24h | hermes-sweeper[bot] 双标签触发 |
| 2026-06-XX+ | 等待 author 补测试或 close |

## 学到的规则

### 桌面端 PR 必做 3 件事

1. **跨平台测试矩阵**：
   - Windows 10/11 + PowerShell + WSL（如果涉及 shell）
   - macOS 13+ + zsh + bash 5
   - Linux (Ubuntu 22.04 LTS + glibc 2.35)
2. **桌面端特定测试**（不仅 unit test）：
   - Tauri / Electron 启动时间
   - 系统托盘 / 通知 API 跨平台差异
   - 文件路径处理（Windows backslash vs Unix slash）
3. **跨平台差异解释**（在 PR body "Platform Considerations" 段）：
   - 哪段代码 Windows-specific / macOS-specific / cross-platform
   - 为什么不能 unified abstraction
   - 维护者 review 时的 platform coverage 风险

### 桌面端 vs Web 端的差异点

```
Web 端:                桌面端:
- 浏览器沙箱           - 系统权限
- 单线程 JS           - 多进程 / IPC
- HTTPS / fetch       - file://, 注册表, 守护进程
- 用户管理凭据         - OS-level keychain
- Service Worker      - 后台进程 / 系统托盘
```

## zsxh1990 应用价值

NousResearch scout-phase。**首次 PR 避免碰桌面端**（除非有完整跨平台测试 setup）。

如果必须做桌面端 PR，模板：
```markdown
## Platform Considerations

### Tested on
- [ ] Windows 10/11 + WSL2 (path: `C:\Users\...`)
- [ ] macOS 13+ (path: `/Users/...`)
- [ ] Ubuntu 22.04 LTS (path: `/home/...`)

### Platform-specific code
- `src/platform/windows.ts` — Windows-specific behavior
- `src/platform/unix.ts` — macOS + Linux unified

### Cross-platform abstraction
- `src/platform/index.ts` — exports `getPlatformRoot()`
- Tests in `tests/platform/` for each OS

### Known issues
- macOS Keychain access requires entitlements (not addressed here)
- Windows path normalization may differ in Cyrillic locale (not tested)
```

## 关联

- 反模式：`research/big-repo-pr-knowledge/anti-patterns/nousresearch-comp-desktop.md`
- 反模式：`research/big-repo-pr-knowledge/anti-patterns/nousresearch-risk-platform-windows.md`
- 同类 PR：#63970 (comp/desktop)
- 对比：`NousResearch-hermes-agent/pr-64639-duplicate-pr.md` (不同 close 模式)
- 调研：`hermes-agent-pr-knowledge/report.md`

## 验证

- ⚠️ confidence=medium（无 deep_read 原文，从 anti-pattern source_pr 反推）
- ✅ 真实 PR URL
- ✅ 双 anti-pattern 关联
- ✅ 桌面端 PR 模板
- ✅ agent_guidelines_applied
