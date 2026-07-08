---
type: Anti-Pattern
key: github-pr-diff-caching
symptom: |
  force push 之后 PR review 显示的还是旧 diff / reviewer 看不出改动
title: "GitHub PR 缓存陷阱 — force push 后 PR diff 不更新"
domain: devops
tags:
  - github
  - pr
  - cache
  - force-push
  - diff
status: published
source: practical-experience
confidence: 0.9
created: 2026-07-08
---

## Problem

force push 分支后，PR diff 仍然显示旧的内容。即使本地 git 显示分支已经更新，GitHub PR 仍然显示无关文件。

## Root Cause

GitHub 缓存 PR diff，不会自动刷新。即使 force push 成功，PR diff 仍然显示旧的比较结果。

## Solution

**方案 1：关闭并重新打开 PR**

```bash
# 关闭 PR
gh api repos/OWNER/REPO/pulls/PR_NUMBER -X PATCH -f state=closed

# 重新打开 PR
gh api repos/OWNER/REPO/pulls/PR_NUMBER -X PATCH -f state=open
```

**方案 2：创建新 PR**

如果方案 1 不管用，关闭旧 PR 并创建新 PR：

```bash
# 关闭旧 PR
gh pr close PR_NUMBER --repo OWNER/REPO

# 创建新 PR
gh pr create --repo OWNER/REPO --head YOUR_BRANCH --base main --title "..."
```

**方案 3：更新 PR base**

```bash
# 更新 PR base 到当前 main
gh api repos/OWNER/REPO/pulls/PR_NUMBER -X PATCH -f base=main
```

## Verification

1. PR diff 只显示本次 commit 修改的文件
2. PR 状态显示 "mergeable" 而不是 "dirty"
3. 无关文件不再出现在 PR diff 中

## Why it matters

GitHub 的 PR diff 缓存机制可能导致调试困难。当 force push 后 PR diff 不更新时，需要手动刷新缓存。

## 注意事项

- 关闭并重新打开 PR 是最可靠的刷新方式
- 创建新 PR 可能导致评论和 review 丢失
- 更新 PR base 可能触发新的 CI 检查
