---
type: Anti-Pattern
key: fork-main-sync-upstream
symptom: PR 包含与本次改动无关的文件，CI 检查报 "diff includes unrelated changes" / "please sync your fork"
title: "Fork 同步陷阱 — main 分支 diverged 导致 PR 包含无关文件"
domain: devops
tags:
  - git
  - fork
  - github
  - pr
  - sync
  - upstream
status: published
source: practical-experience
confidence: 0.95
created: 2026-07-08
---

## Problem

从 fork 提交 PR 后，PR diff 显示了大量无关文件（不是本次 commit 修改的文件）。即使 force push 分支，PR 仍然显示这些无关文件。

## Root Cause

fork 的 `main` 分支与 upstream 的 `main` 分支 diverged：

1. fork main 有 upstream 没有的 commit（如 leaderboard snapshot、其他 PR 的合并）
2. 所有从 fork main 创建的分支都会继承这些 commit
3. PR diff 是 fork 分支与 upstream main 的比较，所以会显示这些无关文件

## Solution

**同步 fork main 到 upstream main：**

```bash
# 1. 添加 upstream remote（如果还没有）
git remote add upstream https://github.com/ORIGINAL/REPO.git

# 2. 获取 upstream main
git fetch upstream main

# 3. 强制更新 fork 的 main 到 upstream 的 main
git push origin upstream/main:main --force
```

**然后重新创建分支：**

```bash
# 4. 从更新后的 fork main 创建新分支
git checkout -b my-new-branch origin/main

# 5. cherry-pick 你的 commit
git cherry-pick <your-commit-sha>

# 6. force push 到 PR 分支
git push origin my-new-branch:pr-branch --force
```

## Verification

1. PR diff 只显示本次 commit 修改的文件
2. PR 状态显示 "mergeable" 而不是 "dirty"
3. CI 检查通过（无关文件不会触发 lint/audit 失败）

## Why it matters

这是 fork PR 的常见陷阱。当 fork main 与 upstream main 不同步时，所有 PR 都会受到影响。这个问题在 GitHub 上很难通过 UI 修复，必须用 git 命令行。

## 注意事项

- `git push origin main --force` 不管用，因为本地 main 和 fork main 已经同步
- 必须用 `upstream/main:main` 显式指定源和目标
- GitHub API 的 `PATCH /repos/.../git/refs/heads/main` 在 diverged 时会报 "not a fast forward"
