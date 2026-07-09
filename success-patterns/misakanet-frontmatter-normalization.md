---
type: Success Pattern
key: misakanet-frontmatter-normalization
description: "批量修复同一类问题：保持一致性，单个 PR 包含多个文件"
success_factors:
  - "修复 Issue #380/379/378 中明确的问题"
  - "保持所有文件的一致性"
  - "保留原始内容不变"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "YAML frontmatter"
  - "质量检查通过"
source_pr: Ikalus1988/MisakaNet#414
metrics:
  additions: 42
  deletions: 3
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #414: convert bare JSON frontmatter to YAML

**背景**: 多个 Issue (#380/379/378) 报告 contrib lessons 的 frontmatter 格式不一致。

**成功因素**:

1. **批量修复**: 一个 PR 修复多个文件的同一类问题
2. **保持一致性**: 所有文件都转换为相同的 YAML 格式
3. **保留内容**: 只修改 frontmatter，不改变课程内容
4. **单一 commit**: 一个干净的 commit

**修复内容**:
```yaml
# 修复前
{"title": "...", "domain": "...", ...}

# 修复后
---
title: ...
domain: ...
---
```

**验收标准**:
- [x] 恰好修改了 3 个文件
- [x] 每个文件第 1 行以 `---` 开头
- [x] YAML 字段包含：title, domain, tags, status, source
- [x] 原始课程内容保留
- [x] 只修改目标文件

## 可复用模式

1. **批量修复**: 一个 PR 修复多个文件的同一类问题
2. **保持一致性**: 所有文件使用相同的格式
3. **保留内容**: 只修改格式，不改变内容
4. **单一 commit**: 保持 PR 干净
