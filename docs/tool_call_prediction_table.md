---
type: Reference
title: Tool Call Prediction Table
description: 基于 PR 复杂度预测工具调用次数，275 case 样本 + 10 实际 PR 校准
version: 1.0.0
created: 2026-07-20
---

# Tool Call Prediction Table

> 基于 275 PR case 样本（20 个仓库）+ 10 个实际 PR 校准。

## 预测公式

```
tool_calls = (base + files×2.5 + additions×0.02 + deletions×0.01)
             × test_mult × ci_mult × new_repo_mult × review_mult
             × efficiency_factor
```

- **效率因子**: 熟悉代码库 = 0.20x, 新代码库 = 0.50x, 完全陌生 = 1.0x

## 预测表

### 简单任务（6-15 calls）

| 任务类型 | 文件 | 新增行 | 预测范围 | 典型工具分布 |
|---------|------|--------|---------|-------------|
| 修 typo | 1 | <10 | 6-8 | bash:4 read:1 edit:2 |
| 改配置 | 1 | <20 | 8-10 | bash:5 read:1 edit:2 |
| 加 badge/链接 | 1 | <5 | 6-8 | bash:4 read:1 edit:2 |
| 翻译文档 | 1 | 50-100 | 10-15 | bash:6 read:2 edit:4 |

### 中等任务（15-30 calls）

| 任务类型 | 文件 | 新增行 | 预测范围 | 典型工具分布 |
|---------|------|--------|---------|-------------|
| Bug fix + 测试 | 2-3 | 50-200 | 15-25 | bash:10 read:3 edit:5 write:2 |
| 小 feature | 3-5 | 100-300 | 20-30 | bash:12 read:4 edit:7 write:3 |
| 搜索优化 | 2-4 | 100-300 | 15-25 | bash:10 read:3 edit:5 write:2 |
| Benchmark 脚本 | 2-3 | 200-400 | 18-28 | bash:12 read:3 edit:5 write:4 |

### 复杂任务（30-60 calls）

| 任务类型 | 文件 | 新增行 | 预测范围 | 典型工具分布 |
|---------|------|--------|---------|-------------|
| 新 CLI 命令 | 3-5 | 300-500 | 30-45 | bash:20 read:5 edit:10 write:5 |
| CI pipeline | 3-5 | 200-400 | 25-40 | bash:18 read:4 edit:8 write:4 |
| 跨文件重构 | 5-10 | 200-500 | 35-55 | bash:25 read:8 edit:12 write:5 |
| 大型 benchmark | 5-8 | 500-1000 | 40-60 | bash:28 read:6 edit:10 write:8 |

### 超大任务（60+ calls）

| 任务类型 | 文件 | 新增行 | 预测范围 | 典型工具分布 |
|---------|------|--------|---------|-------------|
| 新模块开发 | 10-20 | 500-2000 | 60-120 | bash:40 read:12 edit:20 write:10 |
| 架构重构 | 15-30 | 1000-3000 | 80-150 | bash:50 read:15 edit:25 write:12 |
| 全栈 feature | 20+ | 2000+ | 100-200+ | bash:60 read:20 edit:30 write:15 |

## 校准数据（10 个实际 PR）

| PR | 文件 | 新增 | 预测 | 实际 | 效率 |
|----|------|------|------|------|------|
| cross-encoder rerank | 3 | 141 | 51 | 16 | 0.31x |
| typo tolerance | 2 | 201 | 49 | 12 | 0.24x |
| BM25 field weights | 4 | 302 | 61 | 10 | 0.16x |
| merge duplicates | 7 | 116 | 57 | 8 | 0.14x |
| NoiseBench | 3 | 723 | 76 | 14 | 0.18x |
| quality scorer | 7 | 400 | 79 | 18 | 0.23x |
| triage command | 3 | 372 | 59 | 15 | 0.25x |
| Dockerfile | 2 | 27 | 42 | 6 | 0.14x |
| evaluator fix | 2 | 190 | 41 | 8 | 0.20x |
| expansion script | 1 | 332 | 49 | 10 | 0.20x |

**平均效率因子: 0.21x**（熟悉代码库的开发者）

## 使用方法

```bash
# 预测单个 PR
python3 scripts/tool_call_predictor.py --task "feat: add feature" --files 5 --additions 300

# JSON 输出
python3 scripts/tool_call_predictor.py --task "fix: bug" --files 2 --additions 50 --json

# 调整参数
python3 scripts/tool_call_predictor.py --task "docs: update" --files 1 --additions 20 --no-tests --no-review
```

## 复杂度因素权重

| 因素 | 权重 | 说明 |
|------|------|------|
| 文件数 | ×2.5/文件 | 每多一个文件，多 2.5 次工具调用 |
| 新增行 | ×0.02/行 | 100 行 ≈ 2 次额外调用 |
| 删除行 | ×0.01/行 | 删除比新增简单 |
| 测试 | ×1.5 | 需要写/跑测试 |
| CI | ×1.3 | 需要调 CI |
| 新仓库 | ×1.4 | 需要 clone/理解代码库 |
| Review | ×1.2 | 预期有 review 反馈 |
