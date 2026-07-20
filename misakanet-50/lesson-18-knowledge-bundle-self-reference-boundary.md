---
type: Lesson
domain: "architecture"
title: "Knowledge Bundle Self-Reference Boundary: Self ≠ Target"
verification: "metadata-normalized"
source_score: 28
detail_score: 24
generalization_score: 24
redaction_score: 20
total_score: 96
grade: A
status: published
created: 2026-07-20
applies_to:
  - knowledge-bundle
  - mcp-server
  - self-reference
  - api-boundary
  - agent-expectation
related_commits:
  - "zsxh1990/pr-genius@af7d1c0"  # Month 3 P0
  - "zsxh1990/pr-genius@54e2155"  # 当前 HEAD (5 lessons + sync)
related_lessons:
  - lesson-13-glama-private-mcp-verification-gate.md
  - lesson-17-data-snapshot-readme-metric-unification.md
---

# Knowledge Bundle Self-Reference Boundary: Self ≠ Target

> Author: 太阳 (Misaka10004)  
> Created: 2026-07-20  
> Domain: architecture / API boundary  
> Source: Evidence 4 实测 — `get_repo_profile("zsxh1990/pr-genius")` → `{"error": "profile not found"}`(正确行为)

## Problem

**agent 用 MCP server 的 `get_repo_profile` 工具查"我自己这个 repo"会拿到 error**,这看起来像 bug,实际是设计。

agent / owner 经常踩的认知陷阱:

> "为什么我用 pr-genius 查 pr-genius 自己的 profile,系统说找不到?是不是数据丢了?"

```
$ echo '{"jsonrpc":"2.0",...,"name":"get_repo_profile","arguments":{"repo":"zsxh1990/pr-genius"}}' | prgenius-core mcp serve

→ {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\n  \"error\": \"profile not found: zsxh1990/pr-genius\"\n}"}],"isError":false}}
```

**真实情况**:pr-genius **是 knowledge bundle,不是 self-profile repo**。`get_repo_profile` 只面向 **target repo**(你想给哪个仓提 PR),**不返回 bundle 自身**。

这是接口边界,不是缺失。

## Root Cause: 3 类 Repository 身份

任何"PR advisor / contribution helper / analyzer"工具都有 3 种身份:

```
[Type 1] Target repo        - 你想给这个仓提 PR → get_repo_profile 返回它的画像
[Type 2] Bundled data repo  - 工具/系统自己的数据仓 → 不应有 profile
[Type 3] Self-aware tool    - 工具知道自己是什么 → describe 自己,不查自己
```

**pr-genius 是 Type 2 + Type 3 的复合**:

| 维度 | pr-genius 身份 | 行为 |
|---|---|---|
| 数据仓 | knowledge bundle(markdown + frontmatter + case study + anti-pattern) | 数据**关于 target**,**不关于 self** |
| 工具 | MCP server(`prgenius-core mcp serve`) | 知道自己是 `prgenius 1.28.1`,能 describe 自己 |
| 接口契约 | `get_repo_profile(repo)` 只查 `<org>-<repo>/index.md` | self 仓**没有** `zsxh1990-pr-genius/index.md` |

**核心**:**profile 是给"提 PR 前的策略参考",不是给"工具元数据"**。

工具元数据走别的接口:
- `serverInfo.name = "prgenius"`(MCP `initialize` 响应)
- `serverInfo.version = "1.28.1"`
- `instructions` 字段:完整的工具说明

## Concrete Evidence (Evidence 4 实测)

pr-genius v1.28.1 本地 MCP server 实测(2026-07-20 19:17 GMT+8):

### 1. `initialize` 返回工具元数据

```json
{
  "serverInfo": {"name": "prgenius", "version": "1.28.1"},
  "instructions": "PR Genius — Evidence-backed PR contribution advisor. ..."
}
```

→ 工具**知道自己是什么、版本、用途**。

### 2. `tools/list` 返回 8 个 tools,全 readable

```json
[
  {"name": "analyze_pr", "description": "分析 PR 并生成结构化改进建议...", "annotations": {"readOnlyHint": true, ...}},
  {"name": "coach_pr", "description": "Agent PR Dojo: 返回 pass/fail + checklist...", "annotations": {...}},
  {"name": "triage_pr", "description": "Policy-aware PR triage — M1...", "annotations": {...}},
  {"name": "get_repo_profile", "description": "返回仓库画像 (org/name)。", "annotations": {...}},
  {"name": "list_open_prs", "description": "列出所有 final_status=open 的 PR Case Study。", ...},
  {"name": "get_case_study", "description": "返回单个 PR Case Study。", ...},
  {"name": "search_patterns", "description": "按关键词搜 anti-patterns + success-patterns (M1 克莱恩 2026-07-19 新增).", ...},
  {"name": "schema_info", "description": "返回支持的 schema 版本和枚举值。", ...}
]
```

→ 所有 tool description 中文显示正常,UTF-8 编码无损。

### 3. `tools/call get_repo_profile("zsxh1990/pr-genius")` 返回 error

```json
{"content":[{"type":"text","text":"{\n  \"error\": \"profile not found: zsxh1990/pr-genius\"\n}"}],"isError":false}
```

**关键观察**:
- `isError: false` → **不是真错误**,是结构化返回
- `error` 字段在 `content[0].text` 里 → **业务级 message,不是协议级 error**
- 返回结构合法 → MCP 协议握手 + JSON-RPC 序列化**全部成功**

→ **这是正确行为**:`prgenius-core mcp serve` 启动时**只在 repo_root 下找 `zsxh1990-pr-genius/index.md`**,找不到就返回结构化"not found"。

## Concrete Pattern: 怎么区分 3 类 self-reference 错误

| 现象 | 根因 | 修复 |
|---|---|---|
| `profile not found: <self>` | **设计正确** — knowledge bundle 不自建 profile | **预期行为**,改查 target repo |
| `ModuleNotFoundError: No module named 'mcp'` | extras 没装 | `uv pip install "mcp>=1.0"` |
| `'prgenius' is a package and cannot be directly executed` | console_scripts 缺失 | `pip install -e ./prgenius` |
| `Failed to spawn: 'prgenius-core'` | pip 没装成功 | 重装,加 `--break-system-packages` 或用 venv |
| `Failed to validate request: Received request before initialization was complete` | 跳过 MCP 握手 | 先发 `initialize` + `notifications/initialized` |

## Anti-Pattern (3 个常见踩坑)

### Anti-pattern 1: "工具不查自己 → 那就是 bug"

```
"我用 pr-genius 查 pr-genius 的 profile,系统说找不到 → 一定是数据丢了 → 报错"
```

**Fix**:**profile 是 target 维度的概念,不是 self 维度**。MCP server 的"我是谁"走 `serverInfo` + `instructions`,不 profile。

### Anti-pattern 2: "把 self 也建个 profile"

```
"那我在 zsxh1990-pr-genius/index.md 里写个 pr-genius 自己的 profile 不就行了?"
→ 自我引用 → 数据循环 → case study 引用自己的 profile → 反向链接炸
→ "贡献者建议" 变成 "我建议我接受我的 PR"
```

**Fix**:**bundle 自知**——bundle 知道自己是什么,但**不参与自己的评分系统**。这是接口边界。

### Anti-pattern 3: "用 isError 字段判断 self-reference"

```python
result = await mcp_client.call_tool("get_repo_profile", {"repo": "self"})
if result.isError:
    raise ToolError("MCP server broken")  # 错!
```

→ `isError` 字段是协议级,**业务级"not found"放在 `content[0].text` 里**。

**Fix**:
```python
result = await mcp_client.call_tool("get_repo_profile", {"repo": "self"})
content = json.loads(result.content[0].text)
if "error" in content:
    if "profile not found" in content["error"]:
        # 业务级 not found,不是协议级 error
        return None  # 预期行为
```

## Generalization

适用于任何 knowledge bundle / agent tool / analyzer:

| 系统类型 | self 是什么 | target 是什么 | self-reference 行为 |
|---|---|---|---|
| **PR advisor**(pr-genius) | knowledge bundle | 想提 PR 的仓 | self 不查 profile,serverInfo 描述 |
| **RAG system**(self-grow-wiki) | vector DB | 用户 query | self 文档不入主索引(server 元数据走 config) |
| **Static analyzer**(ruff/mypy) | 工具二进制 | 用户项目代码 | 工具不分析自己(self-hosting 例外) |
| **Code formatter**(prettier) | formatter | 用户代码 | 不格式化自己的源文件 |
| **Linter**(ESLint) | rule engine | 用户 JS | 不 lint 自己 |

**核心**:**任何"工具"都有 self vs target 的区分,接口契约必须显式声明**。

## Self-Reference Decision Matrix

写一个新 tool 时,问自己 3 个问题:

1. **self 是什么?** — bundle / tool / engine / formatter?
2. **target 是什么?** — 数据 / 代码 / 用户项目 / 配置?
3. **self == target 是否可能?** — 可能 / 不可能 / 永远不?

| self == target | 行为 |
|---|---|
| **永远不** | self-reference error 设计上正确(本例) |
| **可能但少** | 加 warning + 自指 loop 检测 |
| **正常情况** | 显式处理 self(自指 metadata / self-hosting) |

## Related

- **Evidence 4 实测**(2026-07-20 19:17 GMT+8):`initialize` + `tools/list` + `tools/call` 完整握手通过
- **Lesson 13**:Glama private 部署前 4 evidence gate(本 Lesson 是 evidence 4 的副产品)
- **Lesson 17**:data snapshot / README metric unification(bundle 自身的 metric 怎么管理)
- **MEMORY §🌞 pr-genius Month 3 P0**:`get_repo_profile` self-reference 行为记录

## Verification Notes

- 源可信度 28/30:基于真实 MCP 协议交互实测,owner 第一手经验
- 细节质量 24/25:有完整 JSON-RPC 实测响应 + 5 类错误区分 + 3 个 anti-pattern + decision matrix
- 通用化 24/25:模式适用任何 knowledge bundle / agent tool
- 脱敏 20/20:无敏感信息
- 总分 96/100 = A 级,推送 misakanet 候选