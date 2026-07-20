---
type: Lesson
domain: "evaluation"
title: "ContribAI Replay: 15/15 = 100% Hit Rate — Regression Test for Coach Evaluator"
verification: "metadata-normalized"
source_score: 28
detail_score: 23
generalization_score: 22
redaction_score: 20
total_score: 93
grade: A
status: published
created: 2026-07-20
applies_to:
  - evaluation-pipeline
  - regression-test
  - coach-fit
  - contribai-pattern
related_commits:
  - "zsxh1990/pr-genius@966290c"  # ContribAI replay merge (15 scenarios → coach_fit_report.json)
  - "zsxh1990/pr-genius@ce7fad5"  # evaluator merge rate weighting fix (71% → 84%)
  - "zsxh1990/pr-genius@b42ec91"  # contribai verify task (15/15 = 100% hit rate)
related_lessons:
  - lesson-15-duplicate-detector-trigger-extension.md
---

# ContribAI Replay: 15/15 = 100% Hit Rate — Regression Test for Coach Evaluator

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-20  
> Domain: evaluation pipeline / regression test  
> Source: pr-genius contribai replay(2026-07-20 12:06 → 2026-07-20 14:35, 15 cases 100% hit rate)

## Problem

pr-genius 的 `coach` 命令要判断"PR 该不该提"。但**判断标准是什么?**——只有真实 PR 数据不够,因为:

1. 真实 PR 数据是**已发生事件**,无法验证未来判断的准确性
2. 真实 PR 数据缺少"已知错判"的反例
3. 真实 PR 数据分布偏差(80% 来自 28 个活跃仓,小仓 PR 样本不足)

**ContribAI 提供了解决方案**:**专门合成一批"已知会拒的 PR 模式"作为 regression test**,验证 coach 在 15 个已知失败模式上能正确预警。

pr-genius 实战:**15/15 = 100% hit rate** = coach 在 15 个 ContribAI 反例上全部触发 `close` 判定 → **regression test 通过**。

## Root Cause: Coach Evaluator 的 3 类样本来源

任何 ML/rule-based evaluator 都需要 3 类样本:

| 样本类型 | 用途 | pr-genius 数据来源 |
|---|---|---|
| **真实正例**(merged PR) | 验证"会通过的 PR"被判断为 pass | 真实仓历史 merged PR |
| **真实反例**(closed PR) | 验证"会被关的 PR"被判断为 close | 真实仓历史 closed PR |
| **合成反例**(synthetic) | 验证"已知反模式"100% 命中 | **ContribAI 15 个反模式** |

**第三类(合成反例)是 evaluation pipeline 的关键 baseline**——它定义"coaching 系统对已知风险的灵敏度"。

## ContribAI 15 个反模式清单

```
1.  contribai-archived-repo            - PR 给 archived 仓
2.  contribai-auto-generated-trash     - 含 generated files 没删
3.  contribai-breaking-change-no-migration  - breaking change 无 migration
4.  contribai-design-philosophy-mismatch    - 违反设计哲学
5.  contribai-docs-pr-missing-quickstart    - docs PR 缺 quickstart
6.  contribai-duplicate-pr            - 重复 PR
7.  contribai-ethical-review-failed   - 伦理审查不通过
8.  contribai-first-time-large-repo   - 新 contributor 给巨型仓提 PR
9.  contribai-incomplete-readme-contributing  - README/CONTRIBUTING 不完整
10. contribai-missing-tests           - 缺 test
11. contribai-needs-rfc-first         - 应先 RFC
12. contribai-not-a-real-bug          - 不是真 bug
13. contribai-out-of-scope            - 超出 scope
14. contribai-performance-benchmark-missing  - 性能改动无 benchmark
15. contribai-site-tos-violation      - 违反站点 ToS
```

## Concrete Pattern: 3 步建立 Regression Test

### Step 1: 合成反例数据集

每个反模式写一个 minimal 触发场景:
- `contribai-duplicate-pr`:title `"fix: same as #1234"` + body 引用 #1234 → 期望 coach 输出 `needs_preflight` 或 `close`
- `contribai-missing-tests`:diff stat `[src/foo.py +50]` 无 tests 改动 → 期望 coach 输出 `warn`
- 等等

数据存到 `docs/coach_fit_report.json`,**`fit: "n/a"` 标记**表示"非真实样本"。

### Step 2: 跑 evaluator

```python
# scripts/coach_cases.py
def run_replay_tests():
    results = []
    for case in load_contribai_replay_cases():
        predicted = coach_pr(
            title=case["title"],
            repo=case["repo"],
            body=case["body"],
        )
        expected = case["expected_verdict"]
        results.append({
            "case": case["key"],
            "predicted": predicted["verdict"],
            "expected": expected,
            "hit": predicted["verdict"] in expected,
        })
    hit_rate = sum(r["hit"] for r in results) / len(results)
    return hit_rate
```

### Step 3: 统计 hit rate

pr-genius 实战输出:
- `2026-07-20 12:06`:`966290c` 合并 15 个 ContribAI replay → `total_cases: 267`
- `2026-07-20 14:35`:`b42ec91` 验证 → **15/15 = 100% hit rate**

**Hit rate 100% 是 regression test 的"理论上限"**——合成反例设计时就该 100% 命中,如果 < 100% 说明:
- (a) 反模式规则定义有问题
- (b) coach evaluator 实现 bug
- (c) 反例合成场景不够典型

## Anti-Pattern (3 个常见踩坑)

### Anti-pattern 1: "只用真实 PR 数据做评估"

```
"我们有 252 个真实 PR cases,准确率 83.7%,很好"
→ 没合成反例,真实 PR 偏向"好 case"
→ 评估结果乐观,实际线上对反模式不灵敏
```

**Fix**:真实 + 合成双轨,**合成反例 hit rate 必须报告**。

### Anti-pattern 2: "合成反例混进真实 accuracy 计算"

```
"ContribAI 15 + 真实 252 = 267 cases,准确率 85%"
→ 把 synthetic 当 real 算 → 准确率虚高
```

**Fix**:**synthetic 标 `fit: "n/a"`,从 accuracy 公式中排除**:

```json
{
  "total_cases": 267,
  "counts": {
    "correct": 83,    // real pass predicted as pass
    "close": 128,     // real close predicted as close
    "wrong": 41,      // 错误预测
    "skip": 0,
    "n/a": 15         // ContribAI synthetic, 排除
  },
  "accuracy_pct": 83.7,  // (correct + close) / (correct + close + wrong) = 211/252
  "formula": "(correct + close) / (correct + close + wrong) — excludes n/a"
}
```

### Anti-pattern 3: "合成反例没有明确的 expected_verdict"

```yaml
contribai-duplicate-pr:
  title: "fix: same as #1234"
  body: ""
  # 忘了写 expected_verdict → 测试运行时才知道期望什么
```

**Fix**:每个合成 case **必须显式定义 `expected_verdict`**(`pass` / `warn` / `needs_preflight` / `close` / `reject`):

```yaml
contribai-duplicate-pr:
  title: "fix: same as #1234"
  body: "see #1234"
  expected_verdict: ["needs_preflight", "close"]  # 至少 1 个命中就算 hit
```

## Generalization

适用于任何 evaluator / classifier / scoring system:
- **Code review bot**(合成的 anti-pattern 代码片段)
- **Fraud detection**(合成 fraud 模式)
- **Spam classifier**(合成 spam 文本)
- **Anomaly detection**(合成异常事件)

**核心模式**:合成反例 = 已知 risk pattern + 显式 expected output + 100% hit rate 是 baseline。

## Related

- **pr-genius 实战**:`966290c` (merge) + `b42ec91` (verify) + `ce7fad5` (evaluator fix 71% → 84%)
- **pr-genius Glama 评估报告 §2.C**:ContribAI 数据未落地主仓是 v1.4.0 门槛,现已落地
- **Lesson 15**:duplicate detector 7 triggers(ContribAI 部分 trigger 是 contribai-duplicate-pr 等)
- **Lesson 14**:Check tier 升级模式(regression test 通过后才能升 error)

## Verification Notes

- 源可信度 28/30:基于真实 commit + 真实 hit rate 数据
- 细节质量 23/25:有 15 个反模式清单 + 3 步 SOP + 3 个 anti-pattern + JSON 公式
- 通用化 22/25:模式适用任何 evaluator
- 脱敏 20/20:无敏感信息
- 总分 93/100 = A 级,推送 misakanet 候选