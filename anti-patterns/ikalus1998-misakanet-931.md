---
type: Anti-Pattern
key: feat-voice-add-windows-support-for-voice-hook-scri
description: "feat(voice): add Windows support for voice hook script"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "feat(voice)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#931"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#931: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#931](https://github.com/Ikalus1988/MisakaNet/pull/931)
**作者**: @Ikalus1988
**标签**: area:scripts, shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## Summary

Add Windows support for the voice hook script, enabling Voice Prompts functionality on Windows.

## Changes

### New Files
- **scripts/misakanet_voice_hook.bat** — Windows batch script
- **scripts/misakanet_voice_hook.ps1** — PowerShell script

### Updated Files
- **scripts/misakanet_voice_hook.sh** — Added Windows detection (MSYS2/Cygwin/WSL)

## Windows Support

| Environment | Script | Audio Player |
|-------------|--------|--------------|
| macOS | misakanet_voice_hook.sh | afpla

### Maintainer 关键评论

> @Ikalus1988: ## 🧾 Audit Report — PR #931 (5408cf0)

### 📊 Quality Score

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#931: 已合并 by @Ikalus1988
