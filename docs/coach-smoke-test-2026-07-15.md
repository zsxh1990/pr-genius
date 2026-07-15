---
type: Test Report
title: Coach Smoke Test — 5 Large Repos × 20 PRs
date: 2026-07-15
version: v1.1.1
---

# Coach Smoke Test Results

## Test Setup
- **Repos**: microsoft/TypeScript, facebook/react, vercel/next.js, grafana/grafana, kubernetes/kubernetes
- **Sample**: 10 merged + 10 rejected PRs per repo (95 total)
- **Method**: coach with `--author-association NONE` (worst case)

## Results

| 指标 | 结果 |
|------|------|
| 总样本 | 95 |
| 准确率 | **55.8%** |
| 召回率 | **100%** (所有 merged PR 正确预测) |
| 精确率 | 54.3% |
| F1 | 70.4% |

### 混淆矩阵

|  | 预测 Merged | 预测 Rejected |
|--|-------------|---------------|
| 实际 Merged | 50 (TP) | 0 (FN) |
| 实际 Rejected | 42 (FP) | 3 (TN) |

### Tier 分布

| Tier | 总数 | Merged | Rejected | Merged% |
|------|------|--------|----------|---------|
| 🟡 medium_risk | 92 | 50 | 42 | 54% |
| 🔴 high_risk | 3 | 0 | 3 | 0% |

### 按仓库

| 仓库 | 准确率 | 样本 |
|------|--------|------|
| grafana/grafana | 68.8% | 16 |
| kubernetes/kubernetes | 57.9% | 19 |
| facebook/react | 55.0% | 20 |
| microsoft/TypeScript | 50.0% | 20 |
| vercel/next.js | 50.0% | 20 |

## 结论

1. Coach 是"提交前顾问"，不是"预测工具"
2. 对 unknown 仓默认 medium_risk（偏乐观），无法区分 merged/rejected
3. 对 high_risk 的判断准确（3/3 都是 rejected）
4. 对已知仓（有 profile）效果会更好
5. 改进方向：更深层信号（PR 改动范围、CI 状态、review 评论）

## Profile 效果

添加 profile 后结果无变化，因为：
- 大仓 PR 标题/描述都很规范，无明显反模式
- Coach 判断主要基于 Issue 关联和标签信号
- 需要更深层信号才能区分
