---
type: Anti-Pattern Bundle
title: Anti-Patterns 索引
description: PR 提交流程中的反模式（可检索的失败信号）
version: 0.1.0
created: 2026-07-02
---

# Anti-Patterns 反模式库

> **目的**：当 Agent 遇到 PR 失败信号时，拿报错 / 拒绝语关键词去匹配本库，实现**秒级自愈**。
> **原则**：**只填真实教训**——空着比瞎填有用。宁可少，不要假阳性。

## Schema

每个反模式是 1 个 `anti-patterns/<key>.md`：

```yaml
---
type: Anti-Pattern
key: <unique-slug>
symptom: "<触发报错 / 现象>"     # Agent 拿这个去匹配 CI 输出或评论
root_cause: "<根本原因>"          # 解释为什么发生
trigger_keywords: [<string>]     # 用于 grep 匹配拒绝语 / 报错
fix_action: "<如何修复>"          # 具体行动
fix_command: "<可选：命令>"        # ponytail-style 一行 shell
source_pr: <org>/<repo>#<num>     # 教训来源 PR
prevention: "<预防策略>"          # 下次提 PR 前怎么避免
learned_at: YYYY-MM-DD
---
```

## Agent 调用方式

```python
import re
from pathlib import Path

def self_heal(symptom: str, repo: str) -> str | None:
    """匹配 symptom 到最近的反模式，返回 fix_action."""
    for ap_file in Path("research/big-repo-pr-knowledge/anti-patterns").glob("*.md"):
        fm = parse_frontmatter(ap_file.read_text())[0]
        keywords = fm.get("trigger_keywords", [])
        if any(kw.lower() in symptom.lower() for kw in keywords):
            return f"[Anti-Pattern Match] {fm['key']}: {fm['fix_action']}"
    return None
```

## 已有反模式（11 条）

| Key | 仓 | 信号 |
|---|---|---|
| [uv-cargo-fmt-required](./uv-cargo-fmt-required.md) | astral-sh/uv | "Please run cargo fmt before..." |
| [vite-sapphi-red-instant-close](./vite-sapphi-red-instant-close.md) | vitejs/vite | "I don't think this is useful" |
| [honcho-default-db-module-trap](./honcho-default-db-module-trap.md) | plastic-labs/honcho | `db: AsyncSession = db` 默认参数陷阱 |
| [e2b-feature-not-adding-canned-response](./e2b-feature-not-adding-canned-response.md) | e2b-dev/E2B | "we're not adding this feature to our CLI" |
| [cosmetic-no-user-pain](./cosmetic-no-user-pain.md) | 多仓 | "not seeing any major user pain" / "cosmetic" |
| [breaking-change-no-compat](./breaking-change-no-compat.md) | plastic-labs/honcho | "pretty big breaking change" / "compatibility issues" |
| [upstream-already-implementing](./upstream-already-implementing.md) | astral-sh/uv | "官方自己做了" / upstream implemented |
| [low-value-contribution](./low-value-contribution.md) | patchwork-dev/patchwork-os | "not aligned with project goals" |
| [fork-main-sync-upstream](./fork-main-sync-upstream.md) | 多仓 | PR 包含无关文件 / diverged |
| [fork-pr-ci-permission-error](./fork-pr-ci-permission-error.md) | 多仓 | "Resource not accessible by integration" |
| [github-pr-diff-caching](./github-pr-diff-caching.md) | 多仓 | force push 后 PR diff 不更新 |

## 加入新反模式流程

1. 提 PR 被拒 → 记录 maintainer 评论原话
2. 抽关键词（3-5 个）→ grep 在历史上其他 PR 验证
3. 写 `anti-patterns/<key>.md`（基于真实 PR + 真实拒绝语）
4. 更新本 README 表格

## 不收录标准

- 推测性反模式（"我觉得 X 仓会拒绝..."）→ 不填
- 一次性事件（"那天 vibe coding 撞 maintainer 心情不好"）→ 不填
- 没有 PR 来源的教训 → 不填