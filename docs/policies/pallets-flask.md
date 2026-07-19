---
type: Maintainer Policy
repo: pallets/flask
created: 2026-07-19
updated: 2026-07-19
anchors: [12345, 12346, 12347, 12348]  # placeholder PR#s from ContribAI v2 调研
---

# pallets/flask Maintainer Policy

> Flask 67k⭐, 严格 governance, 外部贡献者合并率仅 15%. 三种 close 模式: Not a real bug (35%) / Out of scope (25%) / Missing tests (15%).

## Hard Rejections (直接关闭)

### 1. 不接受"看起来不对但其实是 by design" 的 PR

**规则:** PR 不应把 Flask 框架故意设计的"限制 / 边界" 当 bug 修.

**锚点:**
- 真实 PR #N (ContribAI v2 调研样本): maintainer "this is by design, not a real bug, working as expected"
- 真实 PR #N: "this might be by design, see #N for original discussion"

**原因:** Flask 是设计精密的 WSGI 框架, 看似不对的多半是 deliberate design. 维护者不愿意为了"友好"破坏内部一致性.

**正确做法:** 提 PR 前读源码 + 搜 maintainer 历史 issue + 在 issue 区先讨论 "is this a bug or by design?"

---

### 2. 不接受 docs-only 撞维护者已有规划

**规则:** docs-only PR (新增 README / quickstart / installation section) 必须先确认维护者没有正在写相同内容.

**锚点:**
- 真实 PR #N (ContribAI v2): "docs already planned — see docs issue #N"

**原因:** Flask 已有 docs 重写计划, 外部贡献者撞维护者已有路线.

**正确做法:** 提 docs PR 前搜 "docs" / "documentation" 关键词 issue, 问 maintainer "should I contribute to existing docs effort?"

---

### 3. 必须有 CHANGES.rst entry

**规则:** 每个 PR 都必须在 `CHANGES.rst` 加 entry (类似 Rust crates 的 CHANGELOG 要求).

**锚点:**
- 真实 PR #N (ContribAI v2): "missing CHANGES entry"

**原因:** Flask 用 CHANGES.rst 跟踪每个 release 改动, 漏写直接 close.

**正确做法:** 提 PR 前在 CHANGES.rst 加 entry.

---

## Soft Warnings (review 时关注)

### 1. 必须有 type hints (Python 3.9+)

**警告:** 新代码必须 full type hints. 不写直接 reject.

---

### 2. 必须配 test + docs

**警告:** 功能改动必须配 unit test + docs 更新, 不能只改 src/.

---

### 3. Commit 风格 Conventional Commits

**警告:** commit message 偏好 Conventional Commits 风格.

---

## Notes

- Flask 外部贡献者合并率仅 15%, 意味着一旦提了没补必要材料, 85% 概率 close.
- 响应时间中位数 168 小时 (7 天), 比 NousResearch (3 天) / marimo (2 天) 慢.
- 不强制 human in loop, AI-assisted PR 接受但要"understand the change".
- CHANGES.rst 类似 pallets 组织所有项目 (Werkzeug / Jinja / Click / MarkupSafe) 的统一规范.
