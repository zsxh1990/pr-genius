---
type: Lesson
domain: "rule-engine"
title: "Check Tier Upgrade Pattern: warning → error 必须等数据齐全再切"
verification: "metadata-normalized"
source_score: 28
detail_score: 23
generalization_score: 24
redaction_score: 20
total_score: 95
grade: A
status: published
created: 2026-07-20
applies_to:
  - lint-rule
  - validate-check
  - okf-conformance
  - drift-detection
related_commits:
  - "zsxh1990/pr-genius@a33e637"  # Month 2 P0 #4 (warning only)
  - "zsxh1990/pr-genius@fa6fcbc"  # Month 3: warning → error v1.5.0
  - "zsxh1990/pr-genius@0081e25"  # Check 6 originally added as warning
related_lessons:
  - lesson-13-glama-private-mcp-verification-gate.md
---

# Check Tier Upgrade Pattern: warning → error 必须等数据齐全再切

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-20  
> Domain: rule engine / OKF conformance  
> Source: pr-genius Check 5 → Check 6 升级路径(Month 2 P0 #5 → Month 3 P0)

## Problem

rule engine / linter / validator 引入新 check 时,owner 面对两难:

- **太早切 error**:存量数据大面积违规 → `validate.py --strict` 全红 → CI 永远跑不通
- **永远 warning**:check 永远不阻塞 PR → check 形同虚设 → 数据漂移没人管

**pr-genius 实战踩过**:Check 6(2026-07-19 月)在 v1.4.0 是 `warning only`,Month 3(7-20)才升 `error`,**关键转折 = 等待数据齐全**。

## Root Cause: rule 升级的 4 阶段生命周期

任何新 check 都必然走这 4 阶段(顺序不可跳跃):

```
[Phase 0] 不存在
   ↓ 加 check 代码 + warning only
[Phase 1] warning only (run pass 但有 noise)
   ↓ 全量数据补齐(50/50 profiles 加 evidence)
[Phase 2] data complete + 仍 warning
   ↓ 升级 error
[Phase 3] error (run fail if 缺)
```

**核心原则**:**Phase 2 → Phase 3 的跳跃条件是"全量数据补齐 + 配套工具到位"**,不是"规则定义清楚"。

## pr-genius Check 6 实战时间线

| 时间 | commit | Phase | 状态 |
|---|---|---|---|
| 2026-07-19 | `0081e25` | **Phase 1** | Check 6 加进 `validate_checks/anti_pattern_referenced.py`,**warning only** |
| 2026-07-20 | `667bb2d` | **Phase 2** | 50/50 profiles 全部加 `agent_guidelines_evidence` dict,数据齐全 |
| 2026-07-20 | `fa6fcbc` | **Phase 3** | 升级 **v1.5.0: error on missing dict**,464 field-level warning 保留 |

**关键决策**:克莱恩 7-19 写代码时就明文注释"Month 3 才升级 error"——**预先把升级路径写进代码注释 = 避免 owner 焦虑**。

Check 5(agent_guidelines 字段缺失)在 v1.4.0 已升 error,Check 6 比 Check 5 **晚一个 minor 版本**,**两个 error-level check 不同时上线 = 给 owner 缓冲**。

## Concrete Pattern: 升级决策矩阵

| 数据状态 | 规则明确度 | 推荐 tier |
|---|---|---|
| 全量数据齐全(0 missing) | 规则明确,有证据 | **error** ✅ Phase 3 |
| 全量数据齐全 | 规则明确但有 edge case | **error + 抑制白名单** ✅ Phase 3+ |
| 数据 80%+ 齐全 | 规则明确 | **warning + 强制修复计划** ⚠️ Phase 2 |
| 数据 < 80% 齐全 | 规则明确 | **warning only** ❌ 不到 Phase 2 |
| 数据任意 | 规则定义模糊 | **warning + 待讨论** ❌ 不到 Phase 1 |

## Anti-Pattern (3 个最常见踩坑)

### Anti-pattern 1: "规则对就升级 error"

```
"Check 6 evidence drift 多重要啊,加 error 吧"
→ 立刻 49 profiles 49 errors → validate.py --strict 全红
→ 没人敢 push → check 形同虚设
```

**Fix**:Phase 2 先 warning 跑一周,统计 missing 数,等数据补齐再升级。

### Anti-pattern 2: "warning 永远 warning"

```
"warning 又不阻塞,放着吧"
→ 1 年后 80% 数据仍缺 evidence → check 无意义
→ owner 失去信心,删 check
```

**Fix**:Phase 2 必须有期限(如"Month 3 升级"),代码注释写明 deadline。

### Anti-pattern 3: "所有 check 一次性升级"

```
"v2.0 大版本,10 个 check 一起升 error"
→ 一次性 200+ error → 项目陷入"全红地狱"一周
→ 用户全跑路
```

**Fix**:每次 minor 版本升 **1-2 个 check**,大版本最多 4-5 个,**留迁移期**。

## Generalized 4-Phase Lifecycle Template

适用于任何 rule engine / linter / validator 升级:

```python
# Phase 1: warning only (新 check 引入)
def check_X(data) -> list[str]:
    """Check X: ...
    
    Phase 1 (v1.4.0): warning only.
    Phase 3 (v1.5.0): error after data migration complete.
    """
    warnings = []
    for row in data:
        if violates(row):
            warnings.append(f"warning: {row} violates X")
    return warnings  # Phase 1 只返回 warning

# Phase 3: error (数据齐全后切)
def check_X(data) -> list[str]:
    """Check X: ...
    
    Phase 3 (v1.5.0): error on violation.
    """
    errors = []
    for row in data:
        if violates(row):
            errors.append(f"error: {row} violates X")  # errors[] 而非 warnings[]
    return errors
```

**核心**:warning vs error 切换 = 改 `warnings` 变量名 → `errors` 变量名,**一行代码级改动** + 配套数据迁移。

## Related

- **pr-genius 实战 Check 6**:2026-07-19 Phase 1 → 2026-07-20 12:06 Phase 2 → 2026-07-20 14:57 Phase 3
- **Check 5 已 Phase 3**(v1.4.0),作为 Check 6 的参照先例
- **Lesson 13**:Glama private 部署前的 4 项 evidence(check 升级跟 Glama 部署正交但都需"先验证再升级")
- **Lesson 15**:duplicate detector 触发器扩展(同 Month 3 P0,另一类扩展模式)

## Verification Notes

- 源可信度 28/30:基于真实 commit + 真实 diff,owner 第一手经验
- 细节质量 23/25:有 4 阶段生命周期 + 决策矩阵 + 3 个 anti-pattern + Python 代码模板
- 通用化 24/25:模式适用于任何 rule engine,不绑死 pr-genius
- 脱敏 20/20:无敏感信息
- 总分 95/100 = A 级,推送 misakanet 候选