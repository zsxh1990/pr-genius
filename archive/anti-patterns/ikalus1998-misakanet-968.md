---
type: Anti-Pattern
key: fixgx1-unify-lesson-directory-contract
description: "fixGX1): unify lesson directory contract"
symptom: "已合并 by @Ikalus1988"
trigger_keywords:
  - "fixgx1)"
fix_action: "TODO: 从 maintainer 评论中提取具体修复步骤"
source_pr: "Ikalus1988/MisakaNet#968"
severity: medium
evidence:
  - "Ikalus1988/MisakaNet#968: 已合并 by @Ikalus1988"
learned_at: 2026-08-13
---

## 反模式说明

**PR**: [Ikalus1988/MisakaNet#968](https://github.com/Ikalus1988/MisakaNet/pull/968)
**作者**: @Ikalus1988
**标签**: area:docs, area:config, area:lessons, shape-safe
**关闭原因**: 已合并 by @Ikalus1988

### PR 描述

## Goal

Fix the 'contribute → visible' loop by ensuring all lessons are in the correct directory.

## Problem

- queue_lesson.py writes to lessons/contrib/
- Search/index reads from lessons/core/ and lessons/contrib/
- But 3 lessons were in lessons/ root (not indexed)

## Changes

1. Move 3 misplaced lessons from lessons/ root to lessons/contrib/:
   - data-quality-three-layer-fix-pattern.md
   - macos-homebrew-python-pip-install-blocked-by-pep-668-externa.md
   - wsl-ntfs-sqlite-update-100x-sl

### Maintainer 关键评论

> @Ikalus1988: ## 🧾 Audit Report — PR #968 (0166e86)

### 📊 Quality Score

> @Ikalus1988: ## 🧾 Audit Report — PR #968 (aca2c3e)

### 📊 Quality Score

### 如何避免

TODO: 从上述评论中总结具体避免步骤

### 历史案例

- Ikalus1988/MisakaNet#968: 已合并 by @Ikalus1988
