---
type: Anti-Pattern
key: fork-pr-ci-permission-error
symptom: |
  CI 检查报 "Resource not accessible by integration"（DCO / star-request / audit / lint 全部红）
title: "Fork PR CI 权限错误 — Resource not accessible by integration"
domain: devops
tags:
  - github
  - ci
  - fork
  - permission
  - integration
  - dco
status: published
source: practical-experience
confidence: 0.9
created: 2026-07-08
---

## Problem

从 fork 提交 PR 后，CI 检查报错：

```
Resource not accessible by integration
```

受影响的检查：
- DCO (Signed-off-by 检查)
- star-request (检查是否 star 了仓库)
- audit (代码审计)
- lint (代码检查)

## Root Cause

GitHub 的 fork PR 权限限制：

1. **fork PR 没有仓库写权限**: fork PR 的 CI 运行在 fork 仓库的上下文中，没有 upstream 仓库的写权限
2. **API 调用需要写权限**: DCO、star-request、audit 等检查需要调用 GitHub API 来设置 commit status 或检查 star 状态
3. **权限不足**: fork PR 的 CI token 没有这些 API 的权限

## Solution

**方案 1：同步 fork main 到 upstream main**

```bash
# 同步 fork main 到 upstream main
git remote add upstream https://github.com/ORIGINAL/REPO.git
git fetch upstream main
git push origin upstream/main:main --force
```

同步后，PR 会变成 "own fork" PR，CI 会有完整的权限。

**方案 2：维护者手动合并**

如果方案 1 不管用，维护者可以手动合并 PR，忽略 CI 权限错误。

**方案 3：使用 GitHub App token**

项目维护者可以创建 GitHub App，提供有写权限的 token 给 CI 使用。

## Verification

1. PR CI 检查不再报 "Resource not accessible by integration"
2. DCO、star-request、audit 等检查正常运行
3. PR 状态显示 "mergeable"

## Why it matters

这是 fork PR 的常见问题。当 fork main 与 upstream main 不同步时，PR 会被视为 "external fork" PR，CI 权限受限。

## 注意事项

- 同步 fork main 是最简单的解决方案
- 维护者手动合并是兜底方案
- GitHub App token 是长期解决方案
