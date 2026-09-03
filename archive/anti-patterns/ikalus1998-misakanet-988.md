---
type: Anti-Pattern
key: docs-add-faq-for-setup-and-contributions
description: "docs: add FAQ for setup and contributions"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "docs"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#988"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#988: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#988](https://github.com/Ikalus1988/MisakaNet/pull/988)
**作者**: @Liona-orph
**标签**: area:docs, docs-only, shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## Summary
- add a 19-question FAQ covering installation, local and remote MCP pairing, search troubleshooting, and contribution workflow
- include copy-pasteable examples for local search, Docker, MCP configuration, lesson submission, and DCO repair
- link the FAQ from the README journey table

## Verification
- `git diff --check`
- FAQ contains 19 numbered questions
- validated all referenced local files exist
- `misakanet-core` isolated environment: `search_knowledge.py "DCO sign-off" --top=3

### Maintainer 关键评论

> @Ikalus1988: PR Genius 分析结果：

- ✅ CI 通过

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#988: 已合并 by @Ikalus1988
