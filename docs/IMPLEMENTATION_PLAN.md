---
type: Documentation
---

# PR-Genius 最小可行实现计划

## 核心原则

**字段可信 = 证据链闭环**

每个评分字段必须：
1. 有明确的数据来源（API调用、文件解析）
2. 有可验证的证据（PR链接、时间戳）
3. 有ground truth验证（已知merged/rejected）
4. 有置信度标注（高/中/低）

---

## Phase 1: 数据闭环（1周）

### 目标
将269个case从"unknown"提升到"有证据"

### 实现

```python
# 1. 数据增强脚本
scripts/enrich_cases.py

# 输入: review-cases/*.json
# 输出: 每个case增加:
{
  "evidence": {
    "pr_url": "https://github.com/...",
    "merged_at": "2026-08-18T...",
    "review_data": {
      "fetched_at": "2026-08-18T...",
      "reviews": [...],
      "comments": [...]
    },
    "verification": {
      "source": "github_api",
      "timestamp": "2026-08-18T...",
      "status": "verified"
    }
  }
}
```

### 验证
```bash
# 运行增强
python scripts/enrich_cases.py

# 验证证据链
python scripts/verify_evidence.py
# 输出: 
# Verified: 269/269
# Missing evidence: 0
# Inconsistent: 0
```

---

## Phase 2: 特征提取（1周）

### 目标
从真实PR数据提取可量化特征

### 核心特征

#### 贡献者视角
```python
features_contributor = {
    # 合并概率预测
    "merge_probability": {
        "author_association": "NONE|CONTRIBUTOR|COLLABORATOR|MEMBER|OWNER",
        "review_engagement": "0|1+",
        "repo_merge_rate": 0.65,
        "pr_size_category": "xs|s|m|l",
        "has_issue_link": True,
        "ci_status": "passing|failing"
    },
    
    # 拒绝预检
    "rejection_risk": {
        "missing_issue_link": False,
        "too_large": False,
        "missing_tests": False,
        "has_negative_labels": False
    }
}
```

#### 维护者视角
```python
features_maintainer = {
    # PR优先级评分
    "triage_score": {
        "impact": 0.4,      # 从label推断
        "urgency": 0.3,     # 从label推断
        "author_trust": 0.2, # 从history计算
        "size": 0.1         # 从additions/deletions
    },
    
    # 贡献者可信度
    "contributor_trust": {
        "merged_prs": 12,
        "rejected_prs": 2,
        "merge_rate": 0.857,
        "response_quality": "good"
    }
}
```

### 实现
```python
# 特征提取器
scripts/extract_features.py

# 输入: 增强后的cases
# 输出: 特征向量 + 标签
{
  "features": {...},
  "label": "merged|rejected",
  "confidence": 0.85
}
```

---

## Phase 3: 评分模型（1周）

### 目标
基于特征训练简单评分模型

### 模型选择
**不用复杂ML**，用**加权规则**：
```python
# 合并概率评分
def merge_probability(features):
    score = 0.0
    
    # 权重: 从历史数据学习
    weights = {
        "author_association": 0.25,
        "human_reviews": 0.35,
        "repo_merge_rate": 0.15,
        "pr_size": 0.10,
        "issue_link": 0.10,
        "ci_status": 0.05
    }
    
    # 计算分数
    score += weights["author_association"] * association_score(features["author_association"])
    score += weights["human_reviews"] * review_score(features["human_reviews"])
    # ...
    
    return {
        "score": score,
        "confidence": calculate_confidence(features),
        "factors": [...]
    }
```

### 验证
```python
# 交叉验证
python scripts/validate_model.py

# 输出:
# Accuracy: 82%
# Precision: 85%
# Recall: 78%
# False Positive: 4.2% (目标 <5%)
```

---

## Phase 4: 证据链闭环（1周）

### 目标
每个评分都有可追溯的证据

### 证据链结构
```json
{
  "score": {
    "value": 0.72,
    "confidence": "high",
    "factors": [
      {
        "name": "human_reviews",
        "value": 1,
        "weight": 0.35,
        "contribution": 0.35,
        "evidence": {
          "source": "github_api",
          "endpoint": "/pulls/331372/reviews",
          "data": [...],
          "fetched_at": "2026-08-18T..."
        }
      }
    ]
  },
  "verification": {
    "ground_truth": "merged",
    "prediction": "merged",
    "correct": true,
    "verified_at": "2026-08-18T..."
  }
}
```

### 实现
```python
# 证据链生成器
scripts/generate_evidence_chain.py

# 输出: 每个评分都有完整证据链
{
  "case_id": "vscode-331372",
  "scores": {...},
  "evidence_chains": [...],
  "verification": {...}
}
```

---

## 最小实现范围

### 第一批（必须）
1. **数据增强脚本** - 将unknown cases转为verified
2. **特征提取器** - 提取核心特征
3. **合并概率评分** - 基于加权规则
4. **证据链生成** - 每个评分有证据

### 第二批（重要）
5. **拒绝预检** - 提交前检查
6. **贡献者可信度** - 基于历史
7. **PR优先级评分** - triage

### 第三批（优化）
8. **时间预测** - 响应时间
9. **信任路径** - 建议路径
10. **自动合并判断** - 资格检查

---

## 验证指标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 数据完整性 | 100% | 所有case有evidence |
| 特征覆盖率 | >90% | 核心特征非空 |
| 合并预测准确率 | >80% | 交叉验证 |
| False Positive | <5% | 预测合并但实际拒绝 |
| 证据链完整度 | 100% | 每个评分有source |

---

## 文件结构

```
pr-genius/
├── review-cases/          # 案例库（已有269个）
├── anti-patterns/         # 反模式（已有599个）
├── profiles/              # 维护者画像（已有4个）
├── evidence/              # 证据链（待创建）
│   ├── vscode-331372.json
│   ├── langchain-39701.json
│   └── ...
├── scripts/
│   ├── enrich_cases.py    # 数据增强
│   ├── extract_features.py # 特征提取
│   ├── score_merge.py     # 合并评分
│   ├── generate_evidence.py # 证据链
│   └── validate.py        # 验证
└── docs/
    ├── IMPLEMENTATION_PLAN.md
    └── ...
```
