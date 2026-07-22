---
type: Lesson
domain: "mcp-server"
title: "MCP stdio Runtime Bug: Static Analysis Misses Field-Path & Dead-Import Failures"
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
  - mcp-server
  - static-analysis-fail
  - stdio-smoke
  - runtime-validation
  - field-path-coercion
related_commits:
  - "zsxh1990/pr-genius@22f3356"  # 当前 HEAD
related_lessons:
  - lesson-11-mcp-typo-pool-x3-merged.md
  - lesson-13-glama-private-mcp-verification-gate.md
  - lesson-19-overfit-hard-gate-holdout-required.md
  - lesson-20-honest-claim-vs-runtime-evidence.md
---

# MCP stdio Runtime Bug: Static Analysis Misses Field-Path & Dead-Import Failures

> Author: 太阳 (Misaka10004)
> Created: 2026-07-22
> Domain: MCP server / runtime validation
> Source: 方舟 35 期众测任务1 评测(2026-07-22, 5 模型 pr-genius 横向对比)
> Trigger: ether2 抓到 3 个 runtime bug(soft_violations 路径错配 + 死导入 + .venv 跳过),其他 4 模型静态分析全漏

## Problem

**MCP server 的"我代码写得对" ≠ "工具调用走得通"**。

常见的认知陷阱:

> "我读了 mcp.py / tools.py 代码,字段路径对、import 没死代码、schema 正确,应该没 bug 吧?"

**错**。MCP server 有 3 类 bug 是静态分析抓不到的,必须 stdio roundtrip 实测:

1. **字段路径错配** — A 模块返回 `violations: [{rule_type}]`,B 模块读 `soft_violations: [...]`,**编译通过,运行空值**
2. **死导入** — `from module import _private_func` 函数签名改了,schema 检查通过,运行 ImportError
3. **路径/正则跳过** — `if '.venv/' in path: continue` 写错顺序,运行时漏掉真文件

35 期任务1 ether2 抓到的 3 个 bug 全是这种**静态看不见、运行时炸**的类别。其他 4 个模型静态分析都没抓到。

## Root Cause: MCP Server 的 3 层验证

MCP server(以 pr-genius `prgenius-core mcp serve` 为例)有 3 层独立验证:

```
[Layer 1] Static analysis     — pyright / mypy / ruff / 读代码
         ↓
[Layer 2] Schema validation   — tools/list 返回 inputSchema 正确
         ↓
[Layer 3] stdio roundtrip     — 真实 initialize + tools/list + tools/call
```

**每 +1 层 = 严 1 档,但抓不同类 bug**:

| Layer | 抓什么 | 抓不到什么 |
|---|---|---|
| **L1 Static** | 类型 / 语法 / 死代码 | 字段路径错配 / 跨模块契约 |
| **L2 Schema** | tools description / inputSchema 字段 | 实际工具调用逻辑 |
| **L3 stdio** | 真实 JSON-RPC 通信 + 工具返回 | (全覆盖) |

**关键**:**L1 + L2 都通过 ≠ L3 通过**。L3 才是终极关。

## Concrete Evidence (35 期任务1 ether2 抓的 3 个 bug)

### Bug 1: `soft_violations` 字段路径错配(ether2 唯一抓到)

`REVIEW_FINDINGS.md §1` 原文:

```
- **Runtime bug (new finding):** `mcp.py` `triage_pr` wrapper reads
  `result["soft_violations"]` / `result["hard_violations"]`, but the underlying
  `triage.py` returns a flat `violations` list where each item has `rule_type ∈
  {"hard","soft"}`. Net effect: MCP `triage_pr` for `warn`/`reject` verdicts always
  renders `recommended_action = "needs_human_review (0 soft rule(s))"` /
  `"blocked_by_policy (0 hard rule(s))"`, and `n_soft`/`n_hard` are silently 0.
  CLI does not have this bug because `cli.py` reads `result["violations"]`.
```

**为什么静态分析抓不到**:
- `mcp.py` 读 `result["soft_violations"]` — 编译通过(mypy 不查跨模块契约)
- `triage.py` 返回 `result["violations"]` — 编译通过
- 两模块独立看都对,**只有 stdio 真实调用 `triage_pr` 时才能发现 n_soft=0/n_hard=0**

**stdio 实测输出**(35 期任务1 ether2 `SMOKE_RESULTS.md §1.4` 原文):

```
| 5 | triage_pr | MisakaNet typo | ❌ `Error executing tool triage_pr: triage_pr() got an unexpected keyword argument 'labels'` |
| 6 | triage_pr | unknown/repo | ❌ same |
| 7 | get_repo_profile | unknown/repo | ✅ `{"error":"profile not found: unknown/repo"}` (correct, not exception) |
```

**修后验证**(同文件 §2.2):

```
| 3 | triage_pr | MisakaNet typo | ✅ verdict='pass' recommended_action='safe_to_review' policy_loaded=True violations=0 |
| 4 | triage_pr | unknown/repo | ✅ verdict='needs_preflight' recommended_action='no_policy_for_repo — run generic preflight checks before opening PR' generic=6 |
```

### Bug 2: 死导入 — `_parse_frontmatter_dict`

同 ether2 `SMOKE_RESULTS.md §1.4`:

```
| 10 | search_patterns | query=duplicate | ❌ `cannot import name '_parse_frontmatter_dict' from 'prgenius.parser'` |
```

**为什么静态分析抓不到**:
- `prgenius/parser.py` 以前有 `_parse_frontmatter_dict` 函数
- 后来被改名 / 删除
- `prgenius/patterns.py` 还 import 这个函数 — ruff 不报(myproject) 也不报,因为 import 路径合法
- 只有运行时 `search_patterns` 真实调用时才 ImportError

### Bug 3: `.venv/` 路径跳过写错

ether2 patch 修复 — `validate.py` 跳过 .venv 假阳:

```python
# before patch (8 errors 全是 .venv/ 假阳)
if path.suffix in {'.py', '.md'}:
    issues.append(...)

# after patch
if '.venv' in str(path) or 'site-packages' in str(path):
    continue
if path.suffix in {'.py', '.md'}:
    issues.append(...)
```

**为什么静态分析抓不到**:
- ruff / mypy 不查 validate.py 自己的逻辑分支
- LLM 静态 review 也看不出来"顺序错了"
- 只有 `python3 validate.py --strict` 实跑,看到 8 errors 全是 `.venv/LICENSE.md` 才意识到

### 4 模型静态分析 vs stdio 实测

| 模型 | 静态分析(读 mcp.py / cli.py) | stdio 实测(MCP server 真实调用) | 抓到 bug 数 |
|---|---|---|---|
| **ether2** | ✅ | **✅** | **3** |
| goblet2 原 | ✅ | ⚠️ stub bundle(12 passed) | 1 (str/Path) |
| goblet2 追测 | ✅ | ⚠️ stub bundle(12 passed) | 1 (继承) |
| flare2 | ✅ | ❌ 沙箱禁止 | 1 (len int,但未进 patch) |
| husk2 | ✅ | ⚠️ LORO + smoke 浅测 | 0 (诚实未查) |

**洞察**:**ether2 抓 3 个 = 其他 4 个之和**。stdio 实测是唯一能抓全 3 类 bug 的方式。

## Concrete Pattern: 怎么写 stdio smoke 测试

### 模式 1: 3-step JSON-RPC handshake

```python
# pseudo-code
import subprocess
import json

def mcp_stdio_smoke(server_cmd: list[str]) -> dict:
    proc = subprocess.Popen(
        server_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Step 1: initialize
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "smoke"}}
    }).encode() + b"\n")
    proc.stdin.flush()

    # Step 2: notifications/initialized (no response expected)
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "method": "notifications/initialized"
    }).encode() + b"\n")
    proc.stdin.flush()

    # Step 3: tools/list
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/list"
    }).encode() + b"\n")
    proc.stdin.flush()

    # Read 2 responses (initialize + tools/list)
    responses = []
    for _ in range(2):
        line = proc.stdout.readline()
        responses.append(json.loads(line))

    return {"initialize": responses[0], "tools_list": responses[1]}
```

### 模式 2: tools/call 真测

```python
# 测 triage_pr(soft_violations bug)
result = mcp_call("tools/call", {
    "name": "triage_pr",
    "arguments": {"repo": "Ikalus1988/MisakaNet", "title": "fix typo", "body": "..."}
})

# 关键断言:n_soft / n_hard / recommended_action 都对
content = json.loads(result["content"][0]["text"])
assert content["n_soft"] > 0 or content["n_hard"] > 0, "soft_violations bug 复发!"
```

### 模式 3: 死导入检测

```python
# 测 search_patterns(_parse_frontmatter_dict bug)
result = mcp_call("tools/call", {
    "name": "search_patterns",
    "arguments": {"query": "duplicate"}
})

assert not result.get("isError"), f"死导入复发: {result}"
assert "hits" in json.loads(result["content"][0]["text"])
```

### 模式 4: 路径跳过验证

```bash
# 测 validate.py 不漏真文件
cd /tmp/pr-genius
python3 validate.py --strict 2>&1 | tee /tmp/validate.log

# 关键断言:errors 数 == expected,不是 .venv/ 假阳
grep -E "ERROR.*\.venv/" /tmp/validate.log  # 应为空
```

## Anti-Pattern (4 个常见踩坑)

### Anti-pattern 1: "读代码 = 实测"

```
"我读 mcp.py / cli.py 字段路径对,没 bug"
```

→ 35 期任务1 ether2 反例:**静态读代码 4 模型都没看到 soft_violations 路径错配**。

**Fix**:stdio smoke 必跑,真 initialize + tools/list + tools/call。

### Anti-pattern 2: "Stub bundle 替代真仓"

```
goblet2 任务1: 12 passed (stub bundle)
```

→ stub 是隔离的 fake 数据,**抓不到跨模块契约 bug**(如 soft_violations 路径错配)。

**Fix**:真仓 shallow clone + `pip install -e .` + stdio smoke。

### Anti-pattern 3: "schema 对 = 调用对"

```
"tools/list 返回 8 tools,inputSchema 正确"
```

→ schema 对 ≠ 调用对。L2 通过 ≠ L3 通过。

**Fix**:L2 + L3 都跑。schema 验证 + 真实 tools/call。

### Anti-pattern 4: "沙箱禁 = 不跑"

```
flare2 任务1: 沙箱禁外部网络 + clone 内 Python → 0 个 stdio 实测
```

→ 沙箱禁网络 ≠ 禁 subprocess。**stdio 是子进程通信,跟网络无关**。

**Fix**:沙箱内 `subprocess.Popen(['python3', '-m', 'prgenius.mcp', 'serve'])` + stdin/stdout pipe 通信。**不需要网络**。

## pr-genius 现状差距 + 上路

### 现状

- `prgenius/tests/test_mcp.py` 有 9 个 tool 注册断言(L1+L2)
- **没有 stdio roundtrip 测试**(L3)
- ether2 抓的 soft_violations bug **没沉淀为 regression test**(35 期任务1 报告里建议过,但 pr-genius 仓还没补)
- LORO + MCP smoke 是两套独立,没合并

### 上路 (Month 4 P0 候选)

| 项 | 实现 | 来源 |
|---|---|---|
| **L1** stdio smoke 脚本 | `scripts/mcp_stdio_smoke.py` — 3-step handshake + 9 tools/call | 学自 ether2 SMOKE_RESULTS.md |
| **L2** soft_violations regression test | `prgenius/tests/test_mcp_triage_fieldpath.py` — 验证 n_soft/n_hard 不静默 0 | 学自 ether2 patch |
| **L3** 死导入检测 | `prgenius/tests/test_mcp_no_dead_imports.py` — import 所有 MCP 路径,捕获 ImportError | 学自 ether2 _parse_frontmatter_dict |
| **L4** MCP stdio verify 集成 | `verification/mcp_stdio.log` — 任务前必跑 + 留日志 | 学自 lesson-20 verification 模板 |
| **L5** Check 9.5 stdio smoke 必跑 | `validate_checks/mcp_stdio.py` — 提 PR 时 stdio smoke 必过 | 类比 Check 6/7/8 |

### pr-genius stdio smoke 应达到的目标

```
$ python3 scripts/mcp_stdio_smoke.py

=== MCP stdio smoke ===
[1/3] initialize              → serverInfo.name=prgenius version=1.28.1
[2/3] tools/list              → 8 tools, all readOnlyHint=True
[3/3] tools/call
  - analyze_pr                → tier='high_risk' (correct)
  - coach_pr                  → tier='high_risk' (correct)
  - triage_pr                 → n_soft=2, n_hard=0 (no field-path bug)
  - get_repo_profile          → known_repo=full profile, unknown_repo=structured error
  - search_patterns           → hits=N (no dead import)
  - list_open_prs             → returns open case studies

exit=0 (all 8 tools/call pass)
```

## Generalization

适用于任何 MCP server / RPC service / 子进程协议:

| 系统类型 | 静态抓不到 | stdio 必测 |
|---|---|---|
| **MCP server**(pr-genius) | 字段路径错配 / 死导入 / 路径跳过 | initialize + tools/list + tools/call |
| **LSP server** | capability 协商 / workspace/symbol 返回 | initialize + didOpen + symbol |
| **gRPC service** | streaming backpressure / trailer status | real client + unary + streaming |
| **CLI subcommand** | exit code 边界 / stderr 缓冲 | spawn + stdin pipe + assert stdout |
| **AI agent protocol** | tool schema vs real call 漂移 | MCP-style 3-step handshake |

**核心**:**任何"代码读了没问题"的声明,都需 stdio roundtrip 验证**。

## MCP stdio Hard Gate Decision Matrix

新 MCP server 上线前,问自己 4 个问题:

1. **L1 static 跑了吗?** — pyright / mypy / ruff 全绿
2. **L2 schema 验证了吗?** — tools/list 返回,description 无乱码,inputSchema 字段对
3. **L3 stdio roundtrip 跑了吗?** — initialize + tools/list + 每个 tool 至少 1 次 tools/call
4. **bug 沉淀为 regression test 了吗?** — ether2 抓的 3 个 bug 应进 test_mcp_*.py

| 4 项都答 | 状态 |
|---|---|
| ✅ 4/4 | **可上线** |
| ⚠️ 3/4 | **可上线但标注 known gap** |
| ❌ ≤ 2/4 | **不上线**,先补 stdio 实测 |

## Related

- **35 期任务1 ether2 `SMOKE_RESULTS.md` §1.4 + §2.2**:3 个 bug 实测 + 修复后 8/8 全绿
- **35 期任务1 ether2 `REVIEW_FINDINGS.md` §1**:soft_violations 路径错配详细分析
- **35 期任务1 ether2 `consolidated_fixes.patch`**:3 个 bug 的合并 patch(115 行)
- **Lesson 11**:MCP typo-pool x3 merged(同 mcp-server 域,静态 vs 动态互补)
- **Lesson 13**:Glama 4 evidence gate(本 lesson 的 deployment 域同质)
- **Lesson 19**:Overfit Hard Gate(本 lesson 的 evaluation 域互补)
- **Lesson 20**:Honest Claim vs Runtime Evidence(本 lesson 的诚实 + 实跑维度同源)

## Verification Notes

- 源可信度 28/30:基于 35 期任务1 5 模型评测 ether2 实跑对比
- 细节质量 24/25:有完整 3 bug 原文 + stdio 输出 + 4 模式 + 4 anti-pattern + decision matrix
- 通用化 24/25:模式适用任何 MCP / LSP / gRPC / CLI 子进程协议
- 脱敏 20/20:无敏感信息
- 总分 96/100 = A 级,推送 misakanet 候选
