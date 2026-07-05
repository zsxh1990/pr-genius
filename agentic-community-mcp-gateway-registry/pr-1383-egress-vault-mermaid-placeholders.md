---
type: PR Case Study
title: agentic-community PR #1383 - docs(egress-vault) fix mermaid render placeholders
description: zsxh1990 第二个 MCP Gateway Registry docs mermaid 渲染修复 PR，1 file 2 lines
pr_number: 1383
pr_url: https://github.com/agentic-community/mcp-gateway-registry/pull/1383
repo: agentic-community/mcp-gateway-registry
author: zsxh1990
status: closed-merged
opened_at: 2026-07-04
merged_at: "2026-07-04T16:28:52Z"
closed_at: "2026-07-04T16:28:52Z"
schema_version: rounds v0.5.0
verified_at: "2026-07-05T04:12:46Z"
evidence_urls:
  - https://github.com/agentic-community/mcp-gateway-registry/pull/1383
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/pulls/1383
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/pulls/1383/files
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/issues/1383/comments
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/pulls/1383/reviews
  - https://api.github.com/repos/agentic-community/mcp-gateway-registry/pulls/1383/commits
confidence: medium  # KNOWN_ISSUES J (新增): case body wrote 'open' but GH API shows `state=closed, merged=True, merged_at=2026-07-04T16:28:52Z`. status now corrected to closed-merged.
rounds:
  - round: 1
    action: open
    delta:
      kind: code_change
      value: "+2 / -2 / 1 file (docs/egress-credential-vault.md L147+L161 <server>/<path> → [server]/[path])"
    response_time_h: 0.05
    maintainer_action: null
    bot_review: []
    blocker: null
    resolution: null
    timestamp: "2026-07-04T04:07:47Z"
close_decision:
  status: pending
  reason: "1 file 2 lines docs typo fix, same pattern as #1382"
  decided_at: null
  actor: zsxh1990
final_status: closed-merged
---

# PR #1383: docs(egress-vault): fix mermaid render of placeholders

> zsxh1990 在 [agentic-community/mcp-gateway-registry#1383](https://github.com/agentic-community/mcp-gateway-registry/pull/1383) 的第二个 docs mermaid 渲染修复 PR。  
> **结果**：🟢 open  
> **价值**：跟 #1382 同 pattern，验证 "mermaid render-broken pool" 有更高命中率。

## PR 内容

**问题**：`docs/egress-credential-vault.md` 两处 mermaid `sequenceDiagram` 块儿 `<server>` 与 `<path>` 被解析为 HTML 标签。  
**方案**：`<server>` → `[server]`，`<path>` → `[path]`。  
**规模**：1 file, 2 line diff（两个 round 都用同一文件）。

## Diff

```diff
-    C->>N: MCP request to /<server>
+    C->>N: MCP request to /[server]
@@ -158,7 +158,7 @@ sequenceDiagram
 ...
-    B->>F: GET /oauth2/egress/connect?server=<path>
+    B->>F: GET /oauth2/egress/connect?server=[path]
```

## CI 反馈

| 时间 | 状态 |
|---|---|
| 04:07 PR open | ✅ |
| (Build Documentation auto-run) | ⏳ in_progress → ✅ success (后验) |
| (Deploy to GitHub Pages auto-run) | ✅ skipped |
| mergeable_state | ✅ `clean` |

## PR Body

```
Fix Mermaid placeholders that can be parsed as HTML tags.

Uses bracketed placeholders so the sequence diagrams render consistently.
```

## 教训内化

### ✅ 成功模式 (复用 + 增量)

跟 #1382 同一路径。增量点：
- **同 PR 日发 2 个不同文件** —— 避免 "TYPO 发现 → 大 patch 凑合一发" 的诱惑
- 每个 PR 各自独立 — 维护者可以选合一个 reject 一个（不绑定）
- 各 1 commit 不交织

### 🔁 Reuse condition

`mermaid-render-broken-pool` 模式 = "含 `<word>` 占位符但缺换行隔离的 sequence diagram"  
→ 一次扫描找到 ≥ 2 处 = 发 2 个独立 PR (而不是 1 个大 patch)  
→ 跟维护者节奏 (小批量、低摩擦、单线 commit) 100% 对齐

## 7/4 Decision Plan

- **T+0-24h**：等 maintainer review
- **T+24h**：如果 0 review，写 check-in comment（友好 bot-friendly）
- **T+7d**：bump candidate if 0 review
- **T+14d**：close-decision (如果 maintainer 没反应)

## 跨 PR 关联 (跟 #1382)

- PR #1382: docs/auth.md (1 line)
- PR #1383: docs/egress-credential-vault.md (2 lines)

→ 都属 "mermaid placeholder 修复" 家族 ✅  
→ 都是 docs-only + 0 runtime 改动 ✅  
→ 都没碰 schema / config / deployment ✅

如果 maintainer 合了一个想 kick 另一个 — 这是个低风险 follow-up 机会。
