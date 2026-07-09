---
type: Success Pattern
key: bilig-docs-relative-paths
description: "文档修复：替换绝对路径为相对路径"
success_factors:
  - "修复文档中的绝对路径问题"
  - "替换为仓库相对路径"
  - "最小化修改：只修改必要的链接"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 通过"
source_pr: proompteng/bilig#441
metrics:
  additions: 4
  deletions: 4
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #441: replace 4 absolute /Users/... paths with repo-relative links

**背景**: 文档中包含绝对路径 `/Users/gregkonush/...`，在 GitHub 上 404。

**成功因素**:

1. **修复明确问题**: 绝对路径在 GitHub 上 404
2. **最小化修改**: 只修改 4 个链接
3. **使用相对路径**: 替换为 `../../../apps/...` 相对路径
4. **单一 commit**: 一个干净的 commit

**修复内容**:
```markdown
# Before
[/Users/gregkonush/...](...)

# After
[../../../apps/...](...)
```

**问题分析**:
- 绝对路径在 GitHub 的 source-tree view 上 404
- 对于不共享相同本地路径的读者来说无法访问
- 看起来像是意外泄露的开发环境，而不是有意的文档

## 可复用模式

1. **修复明确问题**: 找到文档中的明显问题
2. **最小化修改**: 只修改必要的内容
3. **使用标准格式**: 使用仓库相对路径
4. **单一 commit**: 保持 PR 干净
