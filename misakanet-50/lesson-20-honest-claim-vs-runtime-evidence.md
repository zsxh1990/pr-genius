---
type: Lesson
domain: "evaluation"
title: "Honest Claim vs Runtime Evidence: 'Honest + Zero Run' = 6.x, 'Honest + Full Run' = 9+"
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
  - verification-methodology
  - sandbox-constraint
  - honest-disclosure
  - independent-validation
related_commits:
  - "zsxh1990/pr-genius@22f3356"  # 当前 HEAD
related_lessons:
  - lesson-13-glama-private-mcp-verification-gate.md
  - lesson-19-overfit-hard-gate-holdout-required.md
---

# Honest Claim vs Runtime Evidence: 'Honest + Zero Run' = 6.x, 'Honest + Full Run' = 9+

> Author: 太阳 (Misaka10004)
> Created: 2026-07-22
> Domain: evaluation methodology / verification
> Source: 方舟 35 期众测任务1 + 任务2 评测(2026-07-22, 5/4 模型横向对比)
> Trigger: flare2 任务1 第5(6.33) vs 任务2 第1(9.34) — 同模型差距 3 分 = "诚实声明 + 零实跑" vs "诚实声明 + 全实跑"

## Problem

**诚实声明 ≠ 实跑证据**。两者都是必要的,但功能不同:

- **诚实声明** = "沙箱不允许,我没跑" → 透明度 +10,但**不证明任何事**
- **实跑证据** = `verification/pytest.log` 36 passed → 证明事,**且透明**

常见的认知陷阱:

> "我已经诚实声明沙箱没跑了,所以分数应该不扣太多吧?"

**错**。诚实声明是必要条件(不诚实 = 0 分),但**不是充分条件**——"诚实声明 + 零实跑"在综合分上只能拿 6.x。35 期任务1 flare2 就是反例(综合 6.33)。

反过来:

> "我没空诚实声明,直接报数字"

**更错**。不诚实 = 0 分,无论数字多漂亮。

**核心**:**诚实是底线,实跑是加分项**。

## Root Cause: 4 种证据形态的分数区间

35 期任务1 评测 5 模型 + 任务2 评测 4 模型,共 9 个数据点,按"诚实声明 + 实跑日志"分 4 类:

| 形态 | 综合分区间 | 例子 | 特征 |
|---|---|---|---|
| **A. 诚实 + 零实跑** | **6.x** | flare2 任务1 (6.33) | OWNER_GATED 5 项未跑 |
| **B. 诚实 + 部分实跑** | 7.x-8.x | goblet2 任务1 原 (7.00) | RUNTIME_ADDENDUM 部分跑 |
| **C. 诚实 + 全实跑** | 8.x-9.x | husk2 任务1 (8.67) / ether2 任务1 (8.00) | 4 验证日志 + smoke |
| **D. 全实跑 + 部署级 + 契约验证** | **9.x+** | flare2 任务2 (9.34) | 9 日志 + tsc + npm install |

**核心洞察**:flare2 在 A → D 形态间跳了 3 分(6.33 → 9.34)。**同模型,不同形态,3 分差距**。这就是"诚实声明 + 实跑"vs"诚实声明 + 零实跑"的具体差距。

## Concrete Evidence (35 期两任务 9 数据点)

### 任务1 (5 模型 pr-genius, 加权综合)

| 模型 | 诚实声明 | 实跑日志数 | pytest | 形态 | 加权分 |
|---|---|---|---|---|---|
| husk2 | ✅ Glama 未发 | **4 (验证 + LORO + smoke)** | 36 passed | **C** | **8.67** |
| ether2 | ✅ Glama blocked | 1 (smoke) | 36 passed | **C** | 8.00 |
| goblet2 追测 | ✅ Glama blocked | 4 (validation) | 12 passed (stub) | **C** | 8.00 |
| goblet2 原 | ✅ Glama blocked | 1 (RUNTIME) | 12 passed (stub) | **B** | 7.00 |
| **flare2** | ✅ **OWNER_GATED 5 项未跑** | **0** | **未跑** | **A** | **6.33** |

### 任务2 (4 模型 fatal-guard v0.3.0, 加权综合)

| 模型 | 诚实声明 | 实跑日志数 | test pass | 形态 | 加权分 |
|---|---|---|---|---|---|
| **flare2** | ✅ S10 simulated | **9 (redact + verify + node-test + self-test + migrate + cli-sanity + zero-dep + npm-install + tsc)** | **61** | **D** | **9.34** |
| husk2 | ✅ 5 项限制 | 4 (verify + test + self-test + tgz) | 44 | **C** | 9.00 |
| ether2 | ✅ S10 real | (应用副本,日志嵌入) | 45 | **C** | 8.67 |
| goblet2 | ✅ step1-survey | (应用副本) | 47 | **C** | 8.34 |

**洞察**:
- flare2 任务1 形态 A → 任务2 形态 D,加权分从 6.33 跳到 9.34,差距 **+3.01**
- 同样诚实声明(都声明沙箱限制),但任务2 prompt 给的可验证子产物多(9 项独立日志 + tsc + npm install),flare2 的强项被激发
- **prompt 工程密度决定模型能力分布** — 这是另一个 lesson 的根因(暂记)

## Concrete Pattern: 怎么把诚实声明升级到实跑证据

### 模式 1: 沙箱内能跑 → 必跑 + 留日志

```
沙箱能力 → 实跑动作 → 留 verification/*.log → 截最后 20-50 行贴报告
```

**pr-genius 例子**:
```bash
# 沙箱能跑
cd /tmp/pr-genius
python3 -m pytest prgenius/tests/ -q > verification/pytest.log 2>&1
tail -20 verification/pytest.log  # 36 passed in 9.05s
exit=$?
echo "exit=$exit" >> verification/pytest.log
```

**报告模板**:
```markdown
## Verification

| Evidence | 命令 | 结果 |
|---|---|---|
| pytest | `python3 -m pytest prgenius/tests/` | 36 passed (9.05s) |
| validate strict | `python3 validate.py --strict` | 0 err / 0 warn |
| MCP smoke | `npx -y @modelcontextprotocol/inspector ...` | 8 tools visible |
| LORO | `python3 scripts/anti_overfit.py --mode loro` | 80.3% mean (stdev 27%) |
```

### 模式 2: 沙箱内不能跑 → OWNER_GATED + 必跑脚本

**沙箱禁止**(网络 / Python execution / 外部 API)→ 显式 OWNER_GATED:

```markdown
## Owner-Gated Items — 沙箱无法跑、owner 本地必做

> 本 Agent 在 auto-mode 沙箱里被禁止:① 外部网络 ② clone 内 Python ③ glama.ai
> 以下验证**未执行**,不冒认已通过。owner 必须在可信环境按顺序跑完。

### 1. pytest 全绿
\`\`\`bash
cd /path/to/repo
python3 -m pytest tests/ -q
预期:全绿
若红:**先读报错修实现,不要改测试掩盖 bug**
\`\`\`

### 2. validate.py --strict --snapshot
\`\`\`bash
cd /path/to/repo
python3 validate.py --strict --snapshot
预期:0 errors / 0 warnings
\`\`\`
```

**flare2 任务1 错在哪里**:OWNER_GATED 写得很完整,但**没有 verification/ 实跑目录**——沙箱内能跑的他也跑不了,所以 0 个日志。

**husk2 任务1 对比**:也写 OWNER_GATED 限制,但 verification/ 目录有 4 个日志——**沙箱内能跑的都跑了**。

### 模式 3: 部署级实跑 = 源码级 + 安装后级

```bash
# 源码级(标准)
pytest tests/ -v
# → 36 passed

# 安装后级(部署级,flare2 任务2 唯一做了)
pip install -e .
python3 -c "from prgenius.mcp import serve; serve()"
# → argv escape 真测 NUL 字节处理
```

**洞察**:**源码级过了 ≠ 安装后过**。`npm install` 后符号链接 / 权限 / 路径都可能坏。部署级实跑才能完整验证。

### 模式 4: TypeScript 契约验证 (`tsc --noEmit`)

```bash
# 验证 index.d.ts 是用户 API 契约
npx -p typescript@4.9.5 tsc --noEmit prgenius/index.d.ts
# → tsc exit=0
```

**洞察**:`index.d.ts` 是给用户/agent 看的 API 契约,**源码级的 `.py` 文件通过 ≠ 契约类型对**。`tsc --noEmit` 验证契约层,4 模型唯一 flare2 做了。

## Anti-Pattern (4 个常见踩坑)

### Anti-pattern 1: "诚实声明代替实跑"

```
"沙箱无外网,我没法跑,但我保证我的代码是对的"
```

→ **保证 ≠ 证据**。"诚实声明" + "无实跑" = 6.x。

**Fix**:OWNER_GATED 5 项 owner 必跑 + verification/ 至少 1 个能跑的日志。

### Anti-pattern 2: "实跑了但没留日志"

```
"我跑了 pytest,全绿"  # 报告里写
# 但 verification/ 目录是空的
```

→ **"我跑了" = self-claim**,无法独立验证。

**Fix**:留 `verification/pytest.log` + 末尾 `exit=$?`,**让评测方独立 grep**。

### Anti-pattern 3: "OWNER_GATED 写得很长很详细 = 高分"

flare2 任务1 OWNER_GATED 5 项写得**很详细**——预期、命令、若红怎么办都写全——但**沙箱内能跑的没跑** → 综合分 6.33。

→ **OWNER_GATED 详细 ≠ 实跑**。owner 拿到手还要自己跑 5 项,这不是"已交付",是"半成品"。

**Fix**:OWNER_GATED 是**沙箱限制的诚实声明**,**不是实跑替代**。能跑的必跑,跑不了才 OWNER_GATED。

### Anti-pattern 4: "诚实声明 + 真跑 = 满分"

→ **不**。诚实 + 真跑只是 C 形态(8.x-9.x),要 9.x+ 还需要部署级 + 契约验证(D 形态)。

**Fix**:C 形态是基线,D 形态是上限。flare2 任务2 是 D 形态。

## pr-genius 现状差距 + 上路

### 现状

- `validation/anti_overfit.log` 不存在(只有 fit_report.json)
- `validation/lorocv.py` 不存在
- `validation/timesplit.py` 不存在
- 评估 pipeline 没有"诚实声明 + 实跑日志"的 4 形态分级

### 上路 (Month 4 P0 候选)

| 项 | 实现 | 来源 |
|---|---|---|
| **L1** verification/ 目录模板 | `verification/{pytest.log, validate_strict.log, mcp_smoke.log, anti_overfit.log}` | 学自 husk2 任务1 |
| **L2** 4 形态分级 | `data/eval_form_taxonomy.md` — A/B/C/D 4 形态 + 分数区间 | 本 lesson 沉淀 |
| **L3** Check 9 强制 verification 目录存在 | `validate_checks/verification_present.py` — 提 PR 时 verification/ 必含 ≥3 个 .log | 类比 Check 6/7/8 |
| **L4** README §Verification 段 | 模板:4 行表格(pytest / validate / MCP / LORO)+ 截屏贴最后 20 行 | 学自 husk2 |
| **L5** OWNER_GATED 模板 | `templates/OWNER_GATED.md` — 5 项 owner 必跑 + 预期 + 若红 | 学自 flare2 |

### pr-genius 评估形态目标

**当前**:B 形态(诚实 + 部分实跑, RUNTIME_ADDENDUM)
**目标**:D 形态(全实跑 + 部署级 + 契约验证)

```
verification/
├── pytest.log              # 36 passed
├── validate_strict.log     # 0 err / 0 warn
├── mcp_smoke.log           # 8 tools visible + get_repo_profile 实测
├── anti_overfit.log        # LORO + time-split 双验证
├── npm_install_post.log    # 安装后 argv escape 实测
└── tsc_check.log           # tsc 4.9.5 --noEmit exit=0
```

**6 个日志 = D 形态** = 综合 9.x+。

## Generalization

适用于任何 AI agent / 自动化工具 / 提交流程:

| 场景 | A 形态(差) | D 形态(好) |
|---|---|---|
| **AI 提 PR** | "我生成代码了,主人自己测" | "verify 4 证据:pytest / lint / MCP smoke / 真实 diff apply" |
| **众测交付** | "我的方案写完了" | "9 实跑日志 + tsc + npm install 后测" |
| **code review bot** | "我 review 了,有问题" | "运行 ruff + mypy + pytest,贴最后 20 行" |
| **AI 数据分析** | "我分析了,结论是 X" | "跑了 SQL + 验证数据 + 留脚本可复现" |
| **MCP server 部署** | "我有 Dockerfile 了" | "Glama 4 evidence + tsc + npm install" |

**核心**:**诚实声明 + 实跑日志是 AI agent 的"工程契约"**——光有诚实不够,要有证据。

## Honest vs Evidence Decision Matrix

新 AI agent / 工具上线前,问自己 4 个问题:

1. **沙箱内能跑的我跑了吗?** — 必跑 + 留 verification/*.log
2. **沙箱内跑不了的我 OWNER_GATED 了吗?** — 显式列出 + 预期 + 若红
3. **源码级 + 部署级 + 契约级都覆盖了吗?** — D 形态 = 三层都跑
4. **验证日志可独立 grep 吗?** — `tail -20 verification/*.log` 能看到结果

| 4 项都答 | 形态 | 分数 |
|---|---|---|
| ✅ 4/4 | **D** | 9.x+ |
| ⚠️ 3/4 | **C** | 8.x-9.x |
| ❌ 2/4 | **B** | 7.x-8.x |
| ❌ ≤ 1/4 | **A** | < 7 |

## Related

- **35 期任务1 + 任务2 评测**:9 模型横向对比,4 形态分级实证
- **35 期任务1 flare2 OWNER_GATED 5 项**:诚实声明写得详细但零实跑(形态 A 反例)
- **35 期任务2 flare2 9 实跑日志**:诚实 + 全实跑 + 部署级 + 契约(形态 D 范本)
- **Lesson 13**:Glama 4 evidence gate(本 lesson 的 MCP 域同质)
- **Lesson 19**:Overfit Hard Gate(本 lesson 的 evaluation 域互补)
- **MEMORY §🦥 独立验证矩阵方法论**:本 lesson 是 MEMORY 守则的 lesson 化沉淀

## Verification Notes

- 源可信度 28/30:基于 35 期两任务 9 模型横向评测实跑对比
- 细节质量 24/25:有完整 4 形态分数区间 + 9 数据点对比 + 4 模式 + 4 anti-pattern + decision matrix
- 通用化 24/25:模式适用任何 AI agent / 自动化工具 / 提交流程
- 脱敏 20/20:无敏感信息
- 总分 96/100 = A 级,推送 misakanet 候选
