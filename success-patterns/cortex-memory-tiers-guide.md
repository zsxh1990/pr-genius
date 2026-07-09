---
type: Success Pattern
key: cortex-memory-tiers-guide
description: "文档贡献：补充缺失的架构指南"
success_factors:
  - "补充 README 中缺失的架构说明"
  - "详细的四层内存模型解释"
  - "实际的使用示例"
  - "单一 commit，干净的 PR"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "CI 通过"
source_pr: gambletan/cortex#12
metrics:
  additions: 171
  deletions: 0
  commits: 1
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #12: add memory-tiers guide

**背景**: README 中只有一行表格和 ASCII 图，缺少详细的四层内存模型说明。

**成功因素**:

1. **补充缺失文档**: README 中缺少详细的架构说明
2. **详细解释**:
   - Working (RAM): 临时工作内存
   - Episodic: 持久化的原始经验
   - Semantic: 提炼的事实（贝叶斯置信度）
   - Procedural: 程序性知识
3. **实际示例**: 提供了使用示例
4. **单一 commit**: 一个干净的 commit

**关键内容**:
```markdown
# Memory Tiers Guide

## Working Memory (RAM)
Temporary working memory for current session.

## Episodic Memory
Persisted raw experiences with timestamps.

## Semantic Memory
Distilled facts with Bayesian confidence scores.

## Procedural Memory
Procedural knowledge and workflows.
```

## 可复用模式

1. **补充缺失文档**: 找到 README 中缺失的说明
2. **详细解释**: 解释架构的核心概念
3. **添加示例**: 提供实际的使用示例
4. **单一 commit**: 保持 PR 干净
