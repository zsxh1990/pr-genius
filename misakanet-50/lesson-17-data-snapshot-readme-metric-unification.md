---
type: Lesson
domain: "documentation"
title: "Data Snapshot / README Metric Unification: One Auto-Generated Source of Truth"
verification: "metadata-normalized"
source_score: 27
detail_score: 24
generalization_score: 24
redaction_score: 20
total_score: 95
grade: A
status: published
created: 2026-07-20
applies_to:
  - readme-badges
  - metric-snapshot
  - auto-generation
  - okf-conformance
related_commits:
  - "zsxh1990/pr-genius@caa8673"  # 15 auto-generated case studies
  - "zsxh1990/pr-genius@b42ec91"  # AP README auto-gen script
  - "zsxh1990/pr-genius@c853c35"  # 6 contribai demo case studies
related_lessons:
  - lesson-16-contribai-replay-regression-test.md
---

# Data Snapshot / README Metric Unification: One Auto-Generated Source of Truth

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-20  
> Domain: documentation / metric governance  
> Source: pr-genius 指标漂移复盘(2026-07-19) + scripts/* auto-gen(2026-07-20)

## Problem

开源项目的 README 指标最容易漂移:

> "README 写 87% 准确率,JSON 数据源写 83.2% 准确率,CHANGELOG 写 226 cases,snapshot 写 252 cases —— 哪个是真的?"

**pr-genius 实战**(2026-07-19 评估文件 §2.D):

| 来源 | 报告指标 |
|---|---|
| README | 121 cases / 87% |
| `docs/coach_fit_report.json` | 226 cases / 83.2% |
| snapshot 文件 | profiles=40 / case_studies=19 |

**3 个数字 3 个真相 = 0 个真相**。

任何 M3 / Glama public listing 看到这个项目,第一印象 = "这项目自己都不知道自己什么状态"。

## Root Cause: README 漂移的 5 个来源

| 来源 | 漂移原因 | 修复方式 |
|---|---|---|
| 1. 手写 metric | Owner 写 README 时凭印象 | **改为 auto-gen** |
| 2. 多数据源并存 | coach_fit_report.json / snapshot.json / CHANGELOG 各写各的 | **单一 source of truth** |
| 3. 没 validate 链接 badge | `imgs.shields.io/badge/...` 不验证存在 | **validate.py 检查** |
| 4. 数据更新但 README 不更新 | push 完数据忘记同步 README | **CI 强制同步** |
| 5. 历史 README 改不动 | "重构 README 太麻烦" | **auto-gen 模板** |

## pr-genius 实战 4 个 auto-gen 修复

pr-genius Month 3 P0 修了 4 个 auto-gen 工具:

### Tool 1: `scripts/generate_ap_readme.py`(2026-07-20 14:35, `b42ec91`)

**做什么**:扫描 `anti-patterns/*.md` 的 frontmatter → 生成 `anti-patterns/README.md` 索引表(67 条按 category 分组)。

```python
# scripts/generate_ap_readme.py (核心逻辑)
for ap_file in anti_patterns_dir.glob("*.md"):
    fm = parse_frontmatter(ap_file.read_text())
    # 抽取 key / symptom / trigger_keywords
    rows.append({
        "key": fm["key"],
        "symptom": fm.get("symptom", ""),
        "keywords": fm.get("trigger_keywords", []),
        "category": ap_file.stem.split("-")[0],  # contribai / general / vite / etc.
    })
# 按 category 排序 → 写 markdown 表格
```

**效果**:新增 anti-pattern → 跑 `python3 scripts/generate_ap_readme.py` → README 自动更新 → 无人工同步成本。

### Tool 2: 15 auto-gen case studies(2026-07-20 14:43, `caa8673`)

**做什么**:从每个仓的 best JSON case → 自动生成 proper PR Case Study markdown。

```bash
# 流程
for repo in actions/checkout huggingface docker/compose fastapi ...:
    best_case = select_best_json_case(repo)
    generate_markdown(best_case)  # 46 行固定模板
```

**效果**:`case_studies: 35 → 50 (+15)`,`orphans: 51 → 49 (-2)`,无手动写。

### Tool 3: case study ↔ anti-pattern reverse links(2026-07-20 14:35, `b42ec91` Task 11)

**做什么**:每个 case study 自动检测"命中了哪些 anti-pattern"→ 反向插入链接。

**效果**:5/19 case studies auto-matched → 14 remaining have no matching anti-pattern(expected)。

### Tool 4: contribai demo case studies(2026-07-20, `c853c35`)

**做什么**:6 个 contribai 反例 → demo case study(标 `fit: n/a`)+ orphan reduction 57→51。

## Concrete Pattern: 单一 Source of Truth 架构

```
[Source of Truth]      [Auto-gen]               [Output]
coach_fit_report.json ──→ scripts/coach_cases.py ──→ docs/badges/cases.json
                          scripts/coach_cases.py ──→ README "Coach accuracy" line
                          scripts/coach_cases.py ──→ CHANGELOG version note
                          
anti-patterns/*.md   ──→ scripts/generate_ap_readme.py ──→ anti-patterns/README.md

<org>-<repo>/index.md ──→ scripts/count_profiles.py ──→ docs/badges/profiles.json
                          scripts/count_profiles.py ──→ README "Repo profiles" line
```

**核心原则**:**所有 metric 都从一个 JSON / frontmatter 数据源派生,不做手写副本**。

## Anti-Pattern (3 个常见踩坑)

### Anti-pattern 1: "README 写完发版时改一下就行"

```
v1.0 release: README 写 "100 cases"
v1.1 release: README 还是 "100 cases"(没改)
实际 v1.1 = 250 cases
→ 用户看 README 永远停留在 v1.0
```

**Fix**:README metric 改成 `{auto-gen}`,CI 跑 `python3 scripts/update_readme.py` 自动填。

### Anti-pattern 2: "JSON 数据源跟 README 各写各的"

```
docs/coach_fit_report.json: total_cases = 267, accuracy = 83.7%
README: "Coach accuracy: 83.7% (267 cases)" ← 手工同步
→ 一个月后 JSON 改成 280 cases / 84.5%,README 忘改
```

**Fix**:**JSON 是 source of truth,README 全部从 JSON 派生**,README 不允许手写 metric。

### Anti-pattern 3: "auto-gen 脚本写完不跑"

```
"我们有 scripts/update_readme.py,只是没跑"
→ README 还是旧的
→ auto-gen 工具形同虚设
```

**Fix**:auto-gen 跑进 CI:
```yaml
# .github/workflows/ci.yml
- name: Auto-gen README metrics
  run: |
    python3 scripts/generate_ap_readme.py
    python3 scripts/coach_cases.py --update-readme
    git diff --exit-code README.md  # 有 diff 就 fail
```

## 4-Phase Auto-Gen Migration Path

新项目改造 README 漂移的推荐路径:

```
[Phase 1]  列出所有手写 metric 在 README 的位置
           ↓
[Phase 2]  把每个 metric 映射到 source of truth(JSON / frontmatter / 文件计数)
           ↓
[Phase 3]  写 auto-gen 脚本(每个 metric 一个),本地跑通
           ↓
[Phase 4]  接 CI(auto-gen 必跑 + diff 检查)
```

每个 Phase 1-2 天,4 Phase 1 周搞定。

## Generalization

适用于任何开源项目:
- **文档站指标**(README / docs / landing page)
- **Dashboard metric**(Grafana / StatsD / Prometheus)
- **Status page**(incident count / uptime %)
- **API 文档指标**(endpoint count / latency)

**核心模式**:**metric 在哪里出现,就在哪里 auto-gen,不允许手写副本**。

## Related

- **pr-genius 实战**:`caa8673` (case auto-gen) + `b42ec91` (AP README auto-gen + reverse links)
- **评估文件 §2.D**:指标漂移原诊断(2026-07-19)
- **Lesson 16**:ContribAI replay regression test(同 Month 3 P0)
- **Lesson 15**:duplicate detector 触发器扩展(同 Month 3 P0)
- **Lesson 14**:Check tier 升级(Check 5/6 升级时也要同步 update README metric)

## Verification Notes

- 源可信度 27/30:基于真实 commit + 真实漂移现象(评估文件 §2.D)
- 细节质量 24/25:有 4 个 auto-gen 工具详解 + 架构图 + 3 个 anti-pattern + 4-Phase migration path
- 通用化 24/25:模式适用任何文档型 metric
- 脱敏 20/20:无敏感信息
- 总分 95/100 = A 级,推送 misakanet 候选