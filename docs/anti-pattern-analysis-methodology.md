---
type: Research Report
title: "PR 反模式分析 — 从被拒 PR 中提取可复用教训"
domain: development
tags:
  - pr
  - anti-pattern
  - retrospective
  - methodology
  - oss
status: published
source: practical-experience
confidence: 0.9
created: 2026-07-08
---

## Problem

提交了大量外部 PR，但拒绝率很高（60%）。每次被拒都是一个教训，但没有系统化地记录和分析。

## Root Cause

没有建立反模式库，导致：
1. 重复犯同样的错误
2. 无法快速诊断 PR 被拒原因
3. 没有预防检查清单

## Solution

**建立反模式分析流程：**

### 1. 记录维护者评论原话

```markdown
## 案例
- **PR**: repo#123
- **提交内容**: 简要描述
- **拒绝原因**: 维护者原话
```

### 2. 提取关键词（3-5 个）

从维护者评论中提取关键词，用于 grep 匹配：
```yaml
trigger_keywords:
  - "not useful"
  - "cosmetic"
  - "breaking change"
```

### 3. 分类反模式

常见反模式：
- **cosmetic-no-user-pain**: 表面修饰无用户痛点
- **breaking-change-no-compat**: 破坏性变更无兼容性
- **upstream-already-implementing**: 上游已在实现（最有价值！）
- **low-value-contribution**: 低价值贡献

### 4. 建立预防检查清单

```markdown
提 PR 前检查：
- [ ] 有没有对应的 Issue 或 Discussion？
- [ ] 维护者是否认可这是个问题？
- [ ] 改动是否改变现有 API 行为？
- [ ] 维护者的 roadmap 中是否有这个功能？
```

## Verification

1. 反模式库有真实 PR 来源
2. 关键词可以 grep 匹配拒绝语
3. 预防检查清单可以减少重复错误
4. 反模式分析可以秒级自愈

## Why it matters

反模式分析是 PR 质量提升的关键。通过系统化地记录和分析被拒 PR，可以：
1. 避免重复犯错
2. 快速诊断问题
3. 建立预防机制

## 关键洞察

**"官方自己做了" 是最有价值的反模式**：
- 不是失败，而是验证方向正确
- 说明产品嗅觉是对的
- 下次可以先问"是否已经在做"

## 参考

- [pr-genius anti-patterns](https://github.com/zsxh1990/pr-genius/tree/main/anti-patterns)
- [rejected-pr-retrospective](https://github.com/zsxh1990/pr-genius/blob/main/docs/rejected-pr-retrospective.md)
