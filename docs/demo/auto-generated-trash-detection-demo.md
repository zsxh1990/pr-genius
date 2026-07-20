---
type: Demo
title: "Demo 7 — Auto-Generated Trash Detection"
description: "pr-genius MCP demo for detecting AI-generated artifacts in PRs before submission."
version: "1.0.0"
created: "2026-07-19"
schema_version: "OKF v0.1"
---

# Demo 7 — Auto-Generated Trash Detection

> **场景**: AI agent 自动生成了 PR, 但包含了工具产物 (README.md --- / search_knowledge.py --- 等奇怪文件名)。
>
> **反模式**: contribai-auto-generated-trash (AI agent 生成 diff 时没清理)
>
> **验证**: pr-genius contribai_replay.py 100% 命中

## Prompt (给 Agent)

```
我准备给 Ikalus1988/MisakaNet 提一个 docs PR:

title: "docs: add quickstart guide"
body: |
  Add a 5-minute quickstart guide to README.

  Changes:
  - README.md: Add quickstart section
  - README.md ---: Generated diff file

请用 pr-genius MCP 工具分析这个 PR:
1. 这个 PR 有没有问题?
2. 如果有, 我应该怎么修?
```

## 实际输出 (pr-genius MCP `triage_pr`)

```json
{
  "verdict": "reject",
  "repo": "Ikalus1988/MisakaNet",
  "policy_loaded": true,
  "message": "❌ REJECT — 1 hard rule(s) violated",
  "violations": [
    {
      "rule_number": 2,
      "rule_title": "不接受生成器残留文件",
      "rule_type": "hard",
      "evidence": "发现文件名含 --- 的生成器残留文件",
      "anchors": [492, 494, 495]
    }
  ]
}
```

## 建议操作

```bash
# 1. 检查 diff 中的文件名
git diff --stat HEAD~1 | grep -E "---|patch|diff"

# 2. 删除生成器残留文件
rm "README.md ---"
rm "search_knowledge.py ---"

# 3. 重新生成干净的 diff
git add README.md
git commit -m "docs: add quickstart guide"

# 4. 验证 diff 干净
git diff --stat HEAD~1
```

## 反模式触发条件

| 条件 | 检查方法 |
|------|---------|
| 文件名含 `---` | `git diff --stat | grep "---"` |
| 文件名含 `patch` / `diff` | `git diff --stat | grep -E "patch|diff"` |
| markdown 粘进源码 | 检查 .py 文件是否包含 markdown 语法 |

## 预防措施

1. **提交前检查 diff**: `git diff --stat` 确认没有奇怪文件名
2. **清理临时文件**: 删除 `---` 后缀的文件
3. **检查 .gitignore**: 确保临时文件被忽略
4. **使用 pr-genius MCP**: `triage_pr` 会自动检测生成器残留
