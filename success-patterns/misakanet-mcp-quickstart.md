---
type: Success Pattern
key: misakanet-mcp-quickstart
description: "文档+测试+配置示例：完整的功能文档化"
success_factors:
  - "解决 Issue #353 中明确的需求"
  - "完整的文档（设置指南 + 配置示例）"
  - "JSON-RPC 测试覆盖"
  - "README 链接"
repo_requirements:
  - "DCO sign-off (git commit -s)"
  - "YAML frontmatter"
  - "质量检查通过"
source_pr: Ikalus1988/MisakaNet#390
metrics:
  additions: 483
  deletions: 1
  commits: 3
  review_comments: 0
  time_to_merge: "1天"
learned_at: 2026-07-09
---

## 成功案例

### PR #390: MCP Server quickstart — docs + Cursor config + smoke test

**背景**: Issue #353 要求为 MCP Server 添加文档和测试。

**成功因素**:

1. **解决明确需求**: Issue #353 详细描述了需求和验收标准
2. **完整文档**:
   - `docs/mcp.md` — 设置指南（Claude Code, Cursor, Claude Desktop）
   - `.cursor/mcp.json` 配置示例
   - README 链接
3. **测试覆盖**:
   - `tests/test_mcp_server.py` — JSON-RPC 测试
   - 覆盖：initialize, tools/list, tools/call, error handling
4. **单一 commit**: 一个干净的 commit

**验收标准**:
- [x] `docs/mcp.md` 创建，包含设置说明
- [x] README 链接到 MCP 文档
- [x] Cursor `.cursor/mcp.json` 配置示例
- [x] JSON-RPC 测试：search + get_lesson
- [x] 搜索结果返回 path/status/badge
- [x] 默认范围：core + contrib（不含 drafts）

## 可复用模式

1. **Issue 驱动**: 先找到明确的 Issue，再实现
2. **完整文档**: 设置指南 + 配置示例 + README 链接
3. **测试覆盖**: 覆盖主要功能
4. **单一 commit**: 保持 PR 干净
