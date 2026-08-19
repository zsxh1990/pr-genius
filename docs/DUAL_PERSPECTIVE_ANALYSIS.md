---
type: Documentation
---

# PR-Genius 双视角差距分析

## 核心洞察

**PR 审查是双向博弈**：
- 贡献者想：如何让 PR 被合并？
- 维护者想：如何高效管理 PR 流入？

现有工具只覆盖"代码质量"，忽视了**信任**和**流程**维度。

---

## 视角一：贡献者（如何让 PR 被合并）

### 核心问题

```
1. 这个仓库接受什么样的 PR？
2. 维护者关心什么？
3. 我需要先做什么才能提 PR？
4. 我的 PR 会被拒绝吗？
5. 需要等多久才能得到反馈？
6. 如何建立维护者信任？
```

### 现有工具覆盖

| 工具 | 覆盖 | 未覆盖 |
|------|------|--------|
| PR-Agent | 代码质量、描述生成 | 仓库文化、信任路径 |
| Coderabbit | 自动审查、路径指令 | 合并预测、响应时间 |
| Magpie | 多AI对抗 | 贡献者导向建议 |
| Greptile | 评论检查 | 信任分析 |

### 未覆盖维度

#### P0 - 必须有

**1. Merge Probability Prediction（合并概率预测）**
```json
{
  "dimension": "merge_probability",
  "description": "预测 PR 合并概率",
  "inputs": {
    "author_association": "NONE|CONTRIBUTOR|COLLABORATOR|MEMBER|OWNER",
    "review_engagement": "0 reviews → 5% | 1+ human → 70%",
    "repo_merge_rate": 0.65,
    "pr_size": "xs/s/m/l",
    "has_issue_link": true,
    "ci_status": "passing"
  },
  "output": {
    "probability": 0.72,
    "confidence": "high",
    "key_factors": ["human_review_received", "issue_linked"]
  }
}
```

**2. Rejection Pre-check（拒绝预检）**
```json
{
  "dimension": "rejection_precheck",
  "description": "提交前检查会被拒绝的原因",
  "checks": [
    {"rule": "missing_issue_link", "severity": "critical", "repo": "langchain"},
    {"rule": "too_large", "threshold": 1000, "current": 1500},
    {"rule": "missing_tests", "required": true},
    {"rule": "duplicate_pr", "similar_prs": ["#1234", "#1235"]}
  ],
  "verdict": "block",
  "blocking_issues": ["missing_issue_link"]
}
```

#### P1 - 重要

**3. Trust Building Path（信任建立路径）**
```json
{
  "dimension": "trust_building",
  "description": "建立维护者信任的路径",
  "current_trust": 0.1,
  "path": [
    {"step": 1, "action": "参与 Issue 讨论", "effort": "low", "trust_gain": 0.1},
    {"step": 2, "action": "提交小 PR (<50 lines)", "effort": "medium", "trust_gain": 0.2},
    {"step": 3, "action": "修复 review 意见", "effort": "medium", "trust_gain": 0.15},
    {"step": 4, "action": "提交大 PR (>200 lines)", "effort": "high", "trust_gain": 0.3}
  ],
  "estimated_time": "2-4 weeks"
}
```

**4. Time-to-Response Estimate（响应时间预测）**
```json
{
  "dimension": "time_to_response",
  "description": "预测首次响应时间",
  "repo活跃度": "high",
  "维护者平均响应": "4.2 hours",
  "PR类型影响": {
    "bug_fix": "2x faster",
    "feature": "normal",
    "docs": "1.5x faster"
  },
  "预测": "6-12 hours"
}
```

#### P2 - 有用

**5. Repository Culture Guide（仓库文化指南）**
```json
{
  "dimension": "repo_culture",
  "description": "仓库文化指南",
  "rules": [
    {"type": "explicit", "source": "CONTRIBUTING.md", "content": "先开 Issue 讨论"},
    {"type": "implicit", "source": "历史PR分析", "content": "小PR更容易合并"},
    {"type": "label", "source": "标签系统", "content": "size:S 优先审查"}
  ],
  "anti_patterns": [
    {"pattern": "big_pr", "example": ">500 lines", "rejection_rate": 0.8}
  ]
}
```

---

## 视角二：维护者（高效审查和管理 PR）

### 核心问题

```
1. 哪些 PR 需要优先处理？
2. 这个 PR 是否符合仓库标准？
3. 这个贡献者可信吗？
4. 如何分配审查资源？
5. 哪些 PR 可以自动合并？
6. 如何避免审查疲劳？
```

### 现有工具覆盖

| 工具 | 覆盖 | 未覆盖 |
|------|------|--------|
| PR-Agent | 代码审查、标签 | PR排序、贡献者信任 |
| Coderabbit | 自动审查 | 负载均衡、stale检测 |
| Magpie | 多维度审查 | triage评分 |
| Greptile | 状态检查 | 重复检测 |

### 未覆盖维度

#### P0 - 必须有

**1. PR Triage Scoring（PR 优先级评分）**
```json
{
  "dimension": "triage_scoring",
  "description": "PR 优先级评分",
  "scoring_model": {
    "impact": 0.4,      // 对用户的影响
    "urgency": 0.3,     // 时间敏感度
    "author_trust": 0.2, // 贡献者可信度
    "size": 0.1         // PR 大小（小=易审查）
  },
  "output": {
    "score": 85,
    "priority": "high",
    "suggested_reviewer": "core-maintainer",
    "estimated_review_time": "30 min"
  }
}
```

**2. Contributor Trust Score（贡献者可信度评分）**
```json
{
  "dimension": "contributor_trust",
  "description": "贡献者可信度评分",
  "inputs": {
    "history": {
      "merged_prs": 12,
      "rejected_prs": 2,
      "merge_rate": 0.857
    },
    "association": "CONTRIBUTOR",
    "review_engagement": "responds_to_feedback",
    "code_quality": "consistent"
  },
  "output": {
    "trust_score": 0.82,
    "category": "trusted",
    "suggestion": "auto-merge eligible"
  }
}
```

#### P1 - 重要

**3. Auto-merge Eligibility（自动合并资格）**
```json
{
  "dimension": "auto_merge",
  "description": "自动合并资格判断",
  "criteria": [
    {"check": "ci_passing", "status": true},
    {"check": "approvals >= 1", "status": true},
    {"check": "no_changes_requested", "status": true},
    {"check": "contributor_trust >= 0.7", "status": true},
    {"check": "pr_size <= 300", "status": true}
  ],
  "verdict": "eligible",
  "confidence": 0.95
}
```

**4. Review Load Balancing（审查负载均衡）**
```json
{
  "dimension": "load_balancing",
  "description": "审查负载均衡建议",
  "reviewers": [
    {"name": "alice", "load": 5, "expertise": ["python", "api"], "availability": "high"},
    {"name": "bob", "load": 8, "expertise": ["frontend"], "availability": "medium"},
    {"name": "charlie", "load": 3, "expertise": ["infra"], "availability": "high"}
  ],
  "suggestion": "assign to charlie (low load, high availability)"
}
```

#### P2 - 有用

**5. Stale PR Detection（过期 PR 检测）**
```json
{
  "dimension": "stale_detection",
  "description": "过期 PR 检测",
  "criteria": {
    "last_activity_days": 14,
    "author_responded": false,
    "reviewer_requested_changes": true
  },
  "verdict": "stale",
  "suggested_action": "close_with_comment"
}
```

**6. Duplicate Detection（重复 PR 检测）**
```json
{
  "dimension": "duplicate_detection",
  "description": "重复 PR 检测",
  "similar_prs": [
    {"number": 1234, "similarity": 0.89, "status": "open"},
    {"number": 1235, "similarity": 0.76, "status": "merged"}
  ],
  "verdict": "potential_duplicate",
  "suggested_action": "check_if_supersedes"
}
```

---

## 实施路线图

### Phase 1: 贡献者核心 (2周)
1. Merge Probability Prediction
2. Rejection Pre-check

### Phase 2: 维护者核心 (2周)
3. PR Triage Scoring
4. Contributor Trust Score

### Phase 3: 高级功能 (4周)
5. Trust Building Path
6. Time-to-Response Estimate
7. Auto-merge Eligibility
8. Review Load Balancing

### Phase 4: 优化 (2周)
9. Repository Culture Guide
10. Stale/Duplicate Detection

---

## 与现有工具的差异化

| 维度 | PR-Genius | 其他工具 |
|------|-----------|----------|
| **视角** | 双视角（贡献者+维护者） | 单视角（代码审查） |
| **预测** | 合并概率、响应时间 | 无 |
| **信任** | 贡献者可信度、信任路径 | 无 |
| **流程** | triage、负载均衡 | 无 |
| **文化** | 仓库规则、隐性规范 | 部分（Coderabbit） |

**PR-Genius 的独特价值**：填补"信任"和"流程"空白，成为 PR 审查的"操作系统"。
