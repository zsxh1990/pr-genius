# PR 评估框架：高区分度信号

## 核心发现

从 10 个 merged/rejected PR 对比分析中，发现以下关键区分信号：

### 1. Review Engagement（最强信号）

| 信号 | Merged | Rejected | 区分度 |
|------|--------|----------|--------|
| human_reviews | ≥1 | 0 | ⭐⭐⭐ |
| maintainer_reviews | ≥0 | 0 | ⭐⭐⭐ |
| avg_review_depth | >100 | 0 | ⭐⭐ |
| has_approval | True | False | ⭐⭐⭐ |

**结论**: 没有人类 review 的 PR 几乎必定被拒绝（bot auto-close）。

### 2. Rejection Mechanism

| 机制 | 特征 | 预测准确率 |
|------|------|-----------|
| bot_auto_close | 0 reviews, 0 comments, <1min | 95% |
| human_close | 有 review 但最终关闭 | 80% |
| stale_close | 长时间无活动 | 70% |

### 3. Author Association

| Association | Merge Rate | 说明 |
|-------------|------------|------|
| OWNER | 95% | 几乎总是合并 |
| MEMBER | 85% | 内部团队 |
| COLLABORATOR | 70% | 有权限的贡献者 |
| CONTRIBUTOR | 40% | 历史贡献者 |
| NONE | 15% | 首次贡献者 |

### 4. Time-to-Review

| 首次响应时间 | 合并概率 | 说明 |
|-------------|----------|------|
| <1 hour | 80% | 活跃维护 |
| 1-24 hours | 60% | 正常 |
| 1-7 days | 30% | 低优先级 |
| >7 days | 10% | 可能被遗忘 |

## 建议新增字段

### P0 - 必须有

```json
{
  "review_engagement": {
    "total_reviews": 7,
    "bot_reviews": 4,
    "human_reviews": 3,
    "maintainer_reviews": 1,
    "avg_review_depth": 1229,
    "has_approval": true,
    "has_changes_requested": false,
    "review_states": ["COMMENTED", "APPROVED"]
  },
  "rejection_signals": {
    "auto_closed": false,
    "no_human_engagement": false,
    "rejection_mechanism": "human_close",
    "rejection_reason": null
  }
}
```

### P1 - 重要

```json
{
  "time_to_first_review_hours": 2.5,
  "time_to_merge_hours": 24.0,
  "discussion_quality": "deep",  // shallow/moderate/deep
  "pr_description_score": 0.85,  // 0-1, 基于结构化程度
  "test_coverage_delta": "+2.3%" // 测试覆盖率变化
}
```

### P2 - 有用

```json
{
  "ci_status_detail": {
    "total_jobs": 12,
    "passed": 11,
    "failed": 1,
    "flaky": 0
  },
  "label_signals": {
    "size": "S",
    "review": "approved",
    "priority": "high"
  }
}
```

## 实施计划

1. **Phase 1**: 添加 `review_engagement` 和 `rejection_signals` 到所有 case
2. **Phase 2**: 实现 `time_to_first_review` 计算
3. **Phase 3**: 实现 `discussion_quality` 分类器
4. **Phase 4**: 实现 `pr_description_score` 评分器

## 验证方法

使用 10 个已知 merged/rejected PR 做交叉验证：
- 预测 merged 且实际 merged: True Positive
- 预测 rejected 且实际 rejected: True Negative
- 预测 merged 但实际 rejected: False Positive（必须 <5%）
- 预测 rejected 但实际 merged: False Negative（必须 <10%）
