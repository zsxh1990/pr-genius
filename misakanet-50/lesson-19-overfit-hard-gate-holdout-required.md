---
type: Lesson
domain: "evaluation"
title: "Overfit Hard Gate: In-Sample Accuracy Must Pair with Holdout (LORO + Time-Split)"
verification: "metadata-normalized"
source_score: 28
detail_score: 24
generalization_score: 24
redaction_score: 20
total_score: 96
grade: A
status: published
created: 2026-07-22
applies_to:
  - evaluation-pipeline
  - ml-evaluator
  - coach-fit
  - holdout-validation
  - anti-overfit
related_commits:
  - "zsxh1990/pr-genius@22f3356"  # 当前 HEAD (data: coach fit report 356 cases 83%)
  - "zsxh1990/pr-genius@54e2155"  # misakanet index sync v0.5.3
related_lessons:
  - lesson-16-contribai-replay-regression-test.md
  - lesson-13-glama-private-mcp-verification-gate.md
---

# Overfit Hard Gate: In-Sample Accuracy Must Pair with Holdout (LORO + Time-Split)

> Author: 太阳 (Misaka10004)
> Created: 2026-07-22
> Domain: evaluation pipeline / ML evaluator
> Source: 方舟 35 期众测任务1 评测(2026-07-22, 5 模型 pr-genius 横向对比)
> Trigger: husk2 唯一做 LORO + 时间分割 holdout,其他 4 模型连 holdout 都没跑直接报 in-sample 83.7%

## Problem

**In-sample 准确率 = 不可信数字**,除非配 holdout 验证。

任何 ML/rule-based evaluator(包括 pr-genius `coach`)在报"准确率 83.7%"时,owner 都会问:

> "这 83.7% 是过拟合训练集的数字,还是真能预测未见数据的?"

如果只报 in-sample,这就是 self-claim——**分数虚高但无法验证**。

pr-genius 现状:
- `data/coach_fit_report.json` 报 **83% accuracy(356 cases, 27 repos)**——这是 in-sample
- 没配 LORO(Leave-One-Repo-Out)holdout 验证
- 没配时间分割(time-split)holdout 验证
- 任何"我没过拟合"的声明都缺证据

**这就是本 lesson 的根因:评分系统 SCORING.md v0.1 没有"反过拟合"维度**——只评源可信度 + 细节 + 通用化 + 脱敏,**不评 overfit 风险**。

## Root Cause: 4 类样本验证等级

任何 evaluator 的准确率数字都有 4 个等级:

```
[Level 0] In-sample only              — 训练集上 83.7%
                                        ↓ +1 维度
[Level 1] Random split holdout        — 随机切 20% 出来,训练集外验证
                                        ↓ +1 维度
[Level 2] Repo-stratified (LORO)      — 按 repo 切分,留一个 repo 全做测试
                                        ↓ +1 维度
[Level 3] Time-split (temporal)       — 按时间切,用 older 训 newer 测
```

**每 +1 维度 = 严 1 档,数字更可信**。

| Level | 报"准确率 X%"的可信度 | 适用场景 |
|---|---|---|
| 0 (in-sample) | 低 — 过拟合风险未消 | 内部 baseline |
| 1 (random split) | 中 — 随机切不算真泛化 | 早期快速验证 |
| 2 (LORO) | **高** — 跨仓泛化真验证 | **pr-genius 必备** |
| 3 (time-split) | **最高** — 未来数据不漏 | 长期 trustworthy 数字 |

## Concrete Evidence (35 期任务1 husk2 vs 其他 4 模型)

pr-genius 35 期众测 5 模型横向对比中,**唯一做 holdout 验证的是 husk2**:

### husk2 的 anti-overfit log(35 期任务1 `verification/anti_overfit.log` 原文):

```
| tailwindlabs/tailwindcss | 9 | 71.4% | 100.0% | +28.6% |
| anthropics/anthropic-sdk-python | 6 | 100.0% | 100.0% | +0.0% |
| langchain-ai/langgraph | 9 | 100.0% | 100.0% | +0.0% |
| microsoft/TypeScript | 10 | 100.0% | 100.0% | +0.0% |
| microsoft/markitdown | 12 | 100.0% | 100.0% | +0.0% |

## Verdict

⚠️  Potential overfit detected:
  - LORO: repo mongodb/mongo-python-driver held-out accuracy drops 85.8% below rest (threshold 15%)
  - Time-split: astral-sh/ruff newer accuracy drops 33.3%
  - Time-split: goharbor/harbor newer accuracy drops 50.0%
```

### 4 个数字的对比

| 模型 | in-sample | LORO holdout | Time-split | 已知偏差仓 |
|---|---|---|---|---|
| **husk2** | 83.7% | **80.3%** (stdev 26.8%) | **91.1%** (+8.4pp) | mongodb/ruff/harbor/chroma/pydantic(显式列) |
| ether2 | (未跑) | — | — | — |
| goblet2 追测 | (未跑) | — | — | — |
| goblet2 原 | (未跑) | — | — | — |
| flare2 | (未跑) | — | — | — |

**洞察**:
- husk2 报 83.7% in-sample + **80.3% LORO** + **91.1% time-split** = 3 个独立数字交叉验证 → **可信**
- 其他 4 个只报 83.7%(in-sample)→ **数字本身没错,但可信度低**
- husk2 额外列出**已知偏差仓**(mongodb/ruff/harbor)→ 这是工程治理,不是掩盖

## Concrete Pattern: 怎么把 in-sample 升到 Level 2-3

### 模式 1: LORO (Leave-One-Repo-Out) — 跨仓泛化

```python
# pseudo-code
repos = list(all_pr_repos)
results = {}
for held_out_repo in repos:
    train = [pr for pr in all_prs if pr.repo != held_out_repo]
    test = [pr for pr in all_prs if pr.repo == held_out_repo]
    model.fit(train)
    results[held_out_repo] = model.evaluate(test)

mean_holdout = mean(results.values())
print(f"LORO mean: {mean_holdout:.1%}")
# 阈值:drop > 15% vs in-sample = potential overfit
```

**关键**:按 repo 切(不是按 PR 切)——pr-genius 评分规则是**仓级**,跨仓泛化才是真测试。

### 模式 2: Time-Split (时间分割) — 未来数据不漏

```python
# pseudo-code
sorted_prs = sorted(all_prs, key=lambda pr: pr.created_at)
split_idx = int(len(sorted_prs) * 0.5)
train = sorted_prs[:split_idx]   # older half
test = sorted_prs[split_idx:]    # newer half

model.fit(train)
newer_accuracy = model.evaluate(test)
print(f"Time-split (newer): {newer_accuracy:.1%}")
# 阈值:newer 准确率 < train 准确率 - 10pp = future leak 风险
```

**关键**:按时间切(不是随机切)——pr-genius 评分规则会**演进**,时间分割确保 future 数据不漏到训练集。

### 模式 3: 已知偏差仓显式列出

不掩盖 known bias:

```json
{
  "known_biased_repos": {
    "mongodb/mongo-python-driver": "0% accuracy (n=6), release-tool 假阳性",
    "goharbor/harbor": "50% time-split drop, 标签分布漂移",
    "chroma-core/chroma": "文档/代码混合 PR 难以分类",
    "pydantic/pydantic": "v1→v2 API 迁移期规则滞后"
  }
}
```

→ 这些不是"系统失败",是**工程治理的诚实声明**。

## Anti-Pattern (4 个常见踩坑)

### Anti-pattern 1: "只报 in-sample,声称'准确率 83%'"

```
$ python3 -m prgenius coach "feat: ..." --repo org/repo --body "..."
# 输出: ... accuracy: 83.7% (267 cases)
# 没有 holdout 数字
```

**Fix**:**3 个数字必须同时报**——in-sample / LORO / time-split。任何缺一个的 = 数字未完整。

### Anti-pattern 2: "Random split 充 holdout"

```python
# 错:random_split
train, test = train_test_split(all_prs, test_size=0.2)  # 同一仓的 PR 散落两边
```

→ **PR 数据是仓内聚类的**,同一仓的 PR 风格相似,random split 让测试集有"同仓邻居"在训练集 → 高估泛化能力。

**Fix**:**必须按 repo 切(LORO)或按时间切(time-split)**,不能 random。

### Anti-pattern 3: "LORO drop 15% 就说'不可用'"

```
"LORO 准确率从 83.7% 掉到 65%,pr-genius 没用"
```

→ LORO drop **不是失败**,是**系统对未知仓的诚实泛化数字**。65% LORO 比"83.7% 不知真假的 in-sample"更可信。

**Fix**:报告 in-sample + LORO + time-split **3 个数字**,让 owner 自己判断。

### Anti-pattern 4: "把 known bias 仓踢出训练集"

```
"mongodb 准确率 0%,踢了它训练集就 100% 了"
```

→ 这是 **selection bias**——你把不会的删了,留下会的,然后报"准确率 100%"。

**Fix**:**保留 known bias 仓**,显式列出,让 owner 知道"系统对 mongodb 风格不熟"。

## pr-genius 现状差距 + 上路

### 现状

- `data/coach_fit_report.json`:报 83% accuracy,**只有 in-sample**
- 无 LORO 脚本
- 无 time-split 脚本
- 评估 pipeline 没有"3 个数字同时报"的硬约束

### 上路 (Month 4 P0 候选)

| 项 | 实现 | 来源 |
|---|---|---|
| **L1** LORO 脚本 | `scripts/anti_overfit_loro.py` — 按 repo 切,报每仓 + mean + stdev | 学自 husk2 |
| **L2** Time-split 脚本 | `scripts/anti_overfit_timesplit.py` — 按 PR created_at 切,报 older/newer 差 | 学自 husk2 |
| **L3** 已知偏差仓字典 | `data/known_biased_repos.json` — 显式列出 | 学自 husk2 诚实声明 |
| **L4** Check 9 反过拟合 | `validate_checks/anti_overfit.py` — 必跑 LORO + time-split,缺数据 = error | 类比 Check 6/7/8 |
| **L5** README metric 同步 | `coach_fit_report.json` 必含 `in_sample` + `loro` + `time_split` 3 个数字 | 学自 lesson-17 metric unification |

### pr-genius LORO 应达到的目标

```
in_sample:  83%  (267 cases, 40 repos)   ← 现有 baseline
loro:       ~80% (mean, stdev 27%)       ← 跨仓泛化,目标 drop < 15%
time_split: ~91% (newer accuracy)       ← 未来数据不漏,目标 drop < 10pp
```

**3 个数字同时报 = 35 期任务1 husk2 的"反过拟合硬关"模式**。

## Generalization

适用于任何 ML/rule-based evaluator:

| 系统类型 | in-sample 必配 | 为什么 |
|---|---|---|
| **PR coach**(pr-genius) | LORO + time-split | 评分规则是仓级,且会演进 |
| **Code reviewer**(CodeRabbit) | repo-stratified + language-stratified | 跨语言泛化关键 |
| **Test selector**(AI test gen) | file-stratified + time-split | 测试要预测未来 bug |
| **Doc classifier**(RAG) | query-stratified + domain-stratified | query 分布漂移严重 |
| **Lint rule scorer**(ESLint) | rule-stratified + repo-stratified | 不同项目风格差异大 |

**核心**:**任何报"准确率 X%"的系统,3 个数字(in-sample / holdout / time-split)同时报才是 trustworthy**。

## Hard Gate Decision Matrix

新 evaluator 上线前,问自己 4 个问题:

1. **in-sample 是多少?** — 必报
2. **跨仓/跨域 holdout 是多少?** — LORO / repo-stratified
3. **未来数据不漏的验证是多少?** — time-split
4. **known bias 仓/类别显式列了吗?** — 不掩盖

| 4 项都答 | 状态 |
|---|---|
| ✅ 4/4 | **可上线**,进 eval pipeline 硬关 |
| ⚠️ 3/4 | **可上线但标注 known gap** |
| ❌ ≤ 2/4 | **不上线**,先补 holdout 验证 |

## Related

- **35 期任务1 评测**:husk2 `verification/anti_overfit.log`(原文 LORO + time-split 双验证)
- **35 期任务1 评测**:cc-haha 评测报告 §九.1 "反过拟合验证是关键差异化指标"
- **Lesson 13**:Glama 4 evidence gate(本 lesson 的 deployment 域同质)
- **Lesson 16**:ContribAI Replay 15/15 100% hit rate(regression test 维度互补)
- **Lesson 17**:Data Snapshot / README Metric Unification(3 个数字必同时报的工程模板)
- **MEMORY §🦥 独立验证矩阵方法论**:诚实声明 + 实跑日志的诚实 vs 实跑打分规则

## Verification Notes

- 源可信度 28/30:基于 35 期任务1 5 模型横向评测实跑对比,owner 第一手评测
- 细节质量 24/25:有完整 4 模型数字对比表 + 3 模式伪代码 + 4 anti-pattern + decision matrix
- 通用化 24/25:模式适用任何 ML/rule-based evaluator,pr-genius / CodeRabbit / RAG / ESLint
- 脱敏 20/20:无敏感信息(评测报告已脱敏)
- 总分 96/100 = A 级,推送 misakanet 候选
