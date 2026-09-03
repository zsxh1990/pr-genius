---
type: Anti-Pattern
key: docs-azure-remove-stale-tested-image-version
description: "docs(azure): remove stale tested image version"
symptom: "已合并 by @nirinchev"
trigger_keywords:
  - "docs(azure)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "mongodb-js/mongodb-mcp-server#1309"
severity: medium
evidence:
  - "mongodb-js/mongodb-mcp-server#1309: 已合并 by @nirinchev"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [mongodb-js/mongodb-mcp-server#1309](https://github.com/mongodb-js/mongodb-mcp-server/pull/1309)
**作者**: @zsxh1990
**标签**: 无
**关闭原因**: 已合并 by @nirinchev

### PR 描述

## Summary

Remove a stale tested image version from the Azure deployment README.

The Bicep template already defines the default container image version, so the README should avoid repeating a version that can drift.

## Testing

Docs-only change.

### Maintainer 关键评论

> @nirinchev: Apologies - this slipped between the cracks - merged.

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- mongodb-js/mongodb-mcp-server#1309: 已合并 by @nirinchev
