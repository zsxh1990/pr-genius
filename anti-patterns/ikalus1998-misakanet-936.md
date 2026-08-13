---
type: Lesson
title: "feat(voice): add global disable switch"
source: "Ikalus1988/MisakaNet#936"
source_url: "https://github.com/Ikalus1988/MisakaNet/pull/936"
category: pr-failure
severity: medium
learned_at: 2026-08-13
---

## Problem

PR [Ikalus1988/MisakaNet#936](https://github.com/Ikalus1988/MisakaNet/pull/936) 已合并 by @Ikalus1988。

**标题**: feat(voice): add global disable switch
**作者**: @zsxh1990
**状态**: 已合并 by @Ikalus1988

## Root Cause

无 maintainer 评论

## What Happened

## Summary

Adds a global toggle to disable all voice prompts.

Closes #934

## Changes

**`docs/connect.html`**:
- Added global disable toggle (always visible below voice toggle)
- Toggle stores preference in `localStorage` (`misaka-voice-disabled`)
- Shows `MISAKANET_VOICE=0` env var hint when enabled
- Voice toggle greyed out when global disable is active

## Validation

- [x] Global disable toggle persists in localStorage
- [x] Voice disabled when global toggle is on
- [x] Voice toggle greye

## Lesson

TODO: 从上述信息中提炼可复用的教训

## Solution

TODO: 如果有修复方案，在此记录

## Verification

TODO: 如何验证教训已内化
