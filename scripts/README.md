---
type: Index
title: scripts/ — pr-genius 日常维护脚本
description: 每个脚本的用途、调用方法、依赖关系（agent-readable）
version: 0.1.0
created: 2026-07-19
conforms_to: OKF v0.1
---

# scripts/ — 维护脚本索引

> 所有脚本 `stdlib only`（除 `cross_validate.py` / `harvest.py` 走 GitHub REST API 用 `urllib`）。
> 运行前建议：`cd <pr-genius repo root> && export PYTHONPATH=./prgenius/src`。

## 分类速查

### 验证 / 仪表盘
| 脚本 | 用途 | 何时跑 |
|---|---|---|
| `cross_validate.py` | 调 GitHub API 拉 PR + 跟 evaluator 对账，输出准确率 | 改 evaluator 后 / 周度 |
| `dashboard.py` | 列出 6 条 open PR case study + days idle + decision | 每天 / 提 PR 前 |
| `validate.py` (在仓根) | OKF v0.1 自检（frontmatter / 死链 / rounds / index 一致性） | 每次 commit 前 / CI |

### 内容扩充 / 数据采集
| 脚本 | 用途 | 何时跑 |
|---|---|---|
| `daily_content_expand.py` | 每天从 32 个大仓采 50 PR（15 merged / 15 closed / 10 review / 10 first-time），写 case study | cron 20:37 Asia/Shanghai |
| `coach_cases.py` | 跑 prgenius eval 全部 case，对账 predicted vs actual，输出 accuracy | 改 evaluator 后 / 周度 |
| `harvest.py` | 给一个被拒 PR URL → 提取成 anti-pattern 或 lesson draft | 维护者 close 后立即 |

### 数据迁移 / 修复
| 脚本 | 用途 | 一次性？ |
|---|---|---|
| `fix_legacy_cases.py` | legacy v0.1 frontmatter → v0.5.0 schema 迁移（action 枚举 + delta 对象 + close_decision） | **一次性**（已完成） |
| `fix_lesson_yaml.py` | misakanet-50/lesson-*.md 删 stray JSON 行 | **一次性**（已被 v2 取代） |
| `fix_lesson_yaml_v2.py` | 同上 + 处理 multi-line JSON / 空字段 / 紧跟 --- 等边角 | **一次性**（修复完成） |

### 维护周期
| 脚本 | 用途 | 何时跑 |
|---|---|---|
| `heartbeat.py` | 每日 10:00 Asia/Shanghai 自检（validator / orphan / stale / 新 merge 检测）+ 写 /tmp/pr_genius_heartbeat.json | cron 10:00 Asia/Shanghai |

## 详细说明

### cross_validate.py — 交叉验证（最近一次结果 14:31 GMT+8）

```bash
python3 scripts/cross_validate.py --all --limit 5
```

走 GitHub REST API 拉每个 profile 仓的最近 5 条 PR，调 evaluator 评分，跟实际结果对账。

**最近结果**（v1.2.0 era, 14:31 GMT+8）：

| 仓库 | 准确率 | 状态 |
|---|---|---|
| microsoft/markitdown | 100% (20/20) | ✅ |
| langchain-ai/langgraph | 95% (19/20) | ✅ 漏报 1 |
| (汇总) | 90% (54/60) | 整体 |
| onyx-dot-app/onyx | — | ❌ Cannot fetch repo info |
| danny-avila/LibreChat | — | ❌ Cannot fetch repo info |
| goreleaser/nfpm | — | ❌ Cannot fetch repo info |
| python-jsonschema/jsonschema | — | ❌ Cannot fetch repo info |
| woodruffw/zizmor | — | ❌ Cannot fetch repo info |

**已知问题**：5 个仓库 fetch 失败 = 仓名/API 路径问题（待克莱恩复核 owner/repo 命名）。

### dashboard.py — Open PR 跟踪

```bash
python3 scripts/dashboard.py
```

**输出**：所有 `final_status: open` 的 case study，按 days idle 降序。

**最近状态**（14:31 GMT+8, 6 条全 open + 全 stale ≥14d）：

| 20d idle | fastmcp #282, future-agi #778, sourcebot #1383, harbor #2121 |
|---|---|
| 16d idle | mongodb-mcp-server #1309, honcho #801 |
| decision | pending × 6 |

### validate.py — OKF 自检（仓根）

```bash
python3 validate.py --strict
```

**最近结果**：✅ All checks passed（195 .md files / 4 项 check 全绿）。

### daily_content_expand.py — 每日扩展

```bash
python3 scripts/daily_content_expand.py --dry-run     # 不写文件
python3 scripts/daily_content_expand.py --limit 20    # 试跑
python3 scripts/daily_content_expand.py               # 真实跑（cron 默认）
```

**配额**（每轮 50 PR）：
- 15 merged (success-pattern)
- 15 closed-without-merge (anti-pattern)
- 10 review comments (learning)
- 10 first-time contributor

**多源分布**：32 个仓 / Python+TS+Go+Rust / 1k-100k star

### coach_cases.py — 预测 vs 实际

```bash
python3 scripts/coach_cases.py
python3 scripts/coach_cases.py --json
python3 scripts/coach_cases.py --limit 20
```

**最新数据**（2026-07-19, HEAD = 27346433）：
- 226 cases / 28 repos
- Accuracy: 83% (87% @121 → 85% @156 → 83% @226)
- Correct 39% / Close 44% / Wrong 17%

### harvest.py — 被拒 PR 提取

```bash
python3 scripts/harvest.py https://github.com/org/repo/pull/123
python3 scripts/harvest.py org/repo 123 --type lesson
python3 scripts/harvest.py org/repo 123 --type anti-pattern
```

输出 Markdown，可直接 `mv` 进 `anti-patterns/` 或 `misakanet-50/lesson-NN-*.md`。

### heartbeat.py — 每日自检

```bash
python3 scripts/heartbeat.py             # 正常
python3 scripts/heartbeat.py --dry-run   # 不写文件
python3 scripts/heartbeat.py --verbose
```

**Cron**：`0 10 * * *` Asia/Shanghai（每天 10:00）

**8 件事**：
1. 跑 validate.py + 记录 error/warning
2. 清点 profile + case study 数量
3. 检测已 tracked 仓的新 merged PR
4. 更新 KNOWN_ISSUES.md
5. 检测 orphan .md
6. 检查 ≥90d stale 的 case study rounds
7. 写 JSON summary 到 /tmp/pr_genius_heartbeat.json
8. 若新 merge → 写 TODO stub

## 调用顺序建议

```
validate.py           # 任何 commit 前
  ↓
heartbeat.py          # 每天 10:00
  ↓
dashboard.py          # 提 PR 前
  ↓
cross_validate.py     # 改 evaluator 后
coach_cases.py        # 改 evaluator 后
daily_content_expand  # 每天 20:37
harvest.py            # 维护者 close 后立即
```

## 已知限制

1. **5 个仓库 fetch 失败**（onyx / LibreChat / nfpm / jsonschema / zizmor）—— 可能 owner 命名错了或 archived，等克莱恩复核
2. **honcho#801 等 6 条 open 全部 decision=pending 20d+** —— 按 ROUNDS_SCHEMA 7/9 + 7/16 决策点已过，待 close_decision 标记
3. **venv 装包失败**（Debian Python 缺 ensurepip）—— 临时绕道 `PYTHONPATH=./prgenius/src python3 -m prgenius`，待克莱恩授权修 venv

## 版本

- v0.1.0 (2026-07-19)：初版（太阳读完 9 个脚本写索引）
