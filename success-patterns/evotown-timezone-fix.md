---
type: Success Pattern
key: evotown-timezone-fix
description: "Bug 修复：修复未定义变量导致的时区问题"
success_factors:
  - "修复 Issue #88 中明确的 bug"
  - "定位根因：未定义的 _CST 变量"
  - "最小化修改：只修改必要的代码"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 通过"
source_pr: EXboys/evotown#103
metrics:
  additions: 2
  deletions: 2
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #103: use display timezone in chronicle service (fix #88)

**背景**: Issue #88 报告更新后时间仍然显示 UTC。

**成功因素**:

1. **修复明确 bug**: Issue #88 详细描述了问题
2. **定位根因**: `chronicle.py` 使用了未定义的 `_CST` 变量
3. **最小化修改**: 只修改必要的代码
4. **单一 commit**: 一个干净的 commit

**修复内容**:
```python
# Before
"generated_at": datetime.now(_CST).isoformat()

# After
"generated_at": datetime.now(_display_tz()).isoformat()
```

**根因分析**:
- `_CST` 变量未定义，导致 `NameError`
- 使用 `_display_tz()` 函数替代，该函数返回正确的时区

## 可复用模式

1. **Issue 驱动**: 先找到明确的 Issue，再修复
2. **定位根因**: 找到问题的根本原因
3. **最小化修改**: 只修改必要的代码
4. **单一 commit**: 保持 PR 干净
