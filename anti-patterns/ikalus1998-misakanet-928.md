---
type: Lesson
title: "feat(voice): MCP voice hooks for audio prompts on tool use"
source: "Ikalus1988/MisakaNet#928"
source_url: "https://github.com/Ikalus1988/MisakaNet/pull/928"
category: pr-failure
severity: medium
learned_at: 2026-08-13
---

## Problem

PR [Ikalus1988/MisakaNet#928](https://github.com/Ikalus1988/MisakaNet/pull/928) 已合并 by @Ikalus1988。

**标题**: feat(voice): MCP voice hooks for audio prompts on tool use
**作者**: @zsxh1990
**状态**: 已合并 by @Ikalus1988

## Root Cause

> @Ikalus1988: ## DCO Sign-off Required

Please add Signed-off-by to your commits:

## What Happened

## Summary

Add voice feedback to MCP tool responses via PostToolUse hook.
When MisakaNet tools are used, the hook plays matching audio prompts.

Closes #912 (voice prompts playback verification).

## Changes

- **`scripts/mcp_server.py`** — add `voice` field to all tool responses
- **`scripts/mcp_http_server.py`** — add `voice` field to all tool responses
- **`scripts/misakanet_voice_hook.sh`** — PostToolUse hook script
- **`docs/integrations/mcp-voice-hooks.md`** — setup documentation
- **`tes

## Lesson

TODO: 从上述信息中提炼可复用的教训

## Solution

TODO: 如果有修复方案，在此记录

## Verification

TODO: 如何验证教训已内化
