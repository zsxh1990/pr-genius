---
type: Anti-Pattern
key: docs-add-python-typescript-code-style-guidelines
description: "docs: add Python/TypeScript code style guidelines"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "docs"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#994"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#994: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#994](https://github.com/Ikalus1988/MisakaNet/pull/994)
**作者**: @yunaremaia
**标签**: area:docs, docs-only, shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

Closes #903

## Summary

Adds a **Code Style Guidelines** section to `CONTRIBUTING.md`, grounded in the repository's actual tooling:

**Python** (ruff, configured in `pyproject.toml`):
- line-length 100, double quotes, target py310
- rule groups `E/F/I/N/W/UP` (pycodestyle, pyflakes, isort, pep8-naming, warnings, pyupgrade)
- required type hints on public functions/properties, `dict | None` union syntax
- one-line docstrings describing non-obvious return values
- verification commands (`ruff che

### Maintainer 关键评论

无 maintainer 评论

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#994: 已合并 by @Ikalus1988
