---
type: PR Case Study
title: agentic-community PR #1382 - docs(auth) fix mermaid render token placeholder
description: zsxh1990 在 MCP Gateway Registry 提的 docs mermaid 渲染修复 PR，1 file 1 line
pr_number: 1382
pr_url: https://github.com/agentic-community/mcp-gateway-registry/pull/1382
repo: agentic-community/mcp-gateway-registry
author: zsxh1990
status: open
opened_at: 2026-07-04
schema_version: rounds v0.5.0
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+1 / -1 / 1 file (docs/auth.md L186 <token> → [token])"
    response_time_h: 0.05
    maintainer_action: null
    bot_review: []
    blocker: null
    resolution: null
    timestamp: "2026-07-04T04:05:38Z"
close_decision:
  status: pending
  reason: "1 file 1 line docs typo fix, 100% match with prior merged pattern (#1373 + #1375)"
  decided_at: null
  actor: zsxh1990
final_status: open
---

# PR #1382: docs(auth): fix mermaid render of token placeholder

> zsxh1990 在 [agentic-community/mcp-gateway-registry#1382](https://github.com/agentic-community/mcp-gateway-registry/pull/1382) 的 docs typo fix PR。  
> **结果**：🟢 open  
> **价值**：mermaid render 修复 + ponytail-pattern "stdlib/native first" 的扩展。

## PR 内容

**问题**：`docs/auth.md` L186 的 mermaid sequence diagram 里 `<token>` 被 mermaid 解析为 HTML 标签，导致对应文档在 GitHub / 站点侧栏 `Build Documentation` Action 渲染异常。  
**方案**：`<token>` → `[token]`，跟同仓维护者 7/3 已合的 #1373 完全同样的 pattern（`#1373` 把 `<vaulted>` → `[vaulted]`）。  
**规模**：1 file, 1 line diff。

## Diff

```diff
-    Client->>NGINX: 1. API Request<br/>Authorization: Bearer <token>
+    Client->>NGINX: 1. API Request<br/>Authorization: Bearer [token]
```

## CI 反馈

| 时间 | 状态 |
|---|---|
| 04:05 PR open | ✅ |
| (Build Documentation auto-run) | ✅ success |
| (Deploy to GitHub Pages auto-run) | ✅ skipped (non-merge) |

mergeable_state = `clean` — 等 maintainer review。

## PR Body（实际发了）

```
Fix a Mermaid placeholder that can be parsed as an HTML tag.

Matches the existing docs pattern of using bracketed placeholders in sequence diagrams.
```

## 教训内化

### ✅ 成功模式 (重复 #1373 + #1375 路径)

1. **找已合的小 PR 当模板** —— 维护者 7/3 #1373 + #1375 都修了"`<word>` → `[word]`" 同一类错
2. **paragraph 解释 < 50 字** —— 简短精确，不带 AI 标签
3. **单 commit + 单 file + 1-line diff** —— 完全 XS = 高 merge 概率
4. **不动 issue tracking** —— 这类 typo 不用先发"我准备 PR"试探
5. **主仓仓 emoji 节奏 (Bracketed Placeholder 模式)** —— 跟历史上 100% 一致

### 🔁 复用 condition

任何含 mermaid `sequenceDiagram` / `flowchart` 块儿 + 字面 `<word>` token 的 docs，都可以走这条路：
- 单文件 ≤ 4 line
- 1 commit
- 标题 = `docs(<scope>): fix mermaid render of <placeholder>`
- Body 1-2 句

## 7/4 Decision Plan

- **T+0** (open 后 1h 内)：不动；CI clean。等 maintainer review
- **T+24h**：record Round 2 + 写 check-in comment 如果 maintainer 还没看
- **T+7d**：bump (友好 check-in)
- **T+14d**：close-decision 触发点（stale close / 友好退出）
- **T+28d**：如果 merged → 刷新 stats（merged count +1）
