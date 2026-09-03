---
type: Anti-Pattern
key: test-identity-verify-identity-aura-badges-for-all
description: "test(identity): verify Identity Aura badges for all three token types"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "test(identity)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#993"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#993: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#993](https://github.com/Ikalus1988/MisakaNet/pull/993)
**作者**: @yunaremaia
**标签**: shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

Closes #911

## Summary

Adds `workers/identity-aura.test.mjs` — a verification suite for the **Identity Aura badge system**, covering all three token types from the issue scope:

| Token type | Badge verified |
|---|---|
| Static MCP_TOKEN | `MisakaNet MCP — public read-only access` |
| Pairing token (basic identity) | `MisakaNet failure-memory connected` |
| Upgraded identity | Japanese `AIM拡散力場` badge |

**Coverage** (9 tests):
- Static token: exact badge match, missing-token fallback, no-KV 

### Maintainer 关键评论

无 maintainer 评论

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#993: 已合并 by @Ikalus1988
