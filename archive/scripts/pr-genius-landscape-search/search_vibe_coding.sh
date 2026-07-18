#!/usr/bin/env bash
# search_vibe_coding.sh — 搜 vibe-coding / AI-assisted PR / AI contributor 类仓
# 用途：找「AI 时代 PR 贡献」上下文（不是直接同类，但共享时代背景）
# 数据源：GitHub 匿名 search API
# 已知状态（2026-07-18 23:55 GMT+8）：
#   - 命中 46820 个 total
#   - top3: coleam00/context-engineering-intro(13.7k), cloudflare/vibesdk(5.2k),
#           filipecalegario/awesome-vibe-coding(5k), shanraisshan/claude-code-best-practice(63k)
#   - 全部非同类（都是 AI 编程工具/教程类，不沉淀 PR 经验）
set -euo pipefail

QUERY='%22vibe+coding%22+OR+%22AI+contributor%22+OR+%22AI-assisted+PR%22+OR+%22AI+contribution%22'
PER_PAGE="${PER_PAGE:-15}"

curl -s "https://api.github.com/search/repositories?q=${QUERY}&sort=stars&order=desc&per_page=${PER_PAGE}" \
  --max-time 15 | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"total={d.get('total_count', 0)}\")
for r in d.get('items', []):
    print(f\"⭐{r['stargazers_count']:>6}  {r['full_name']:50}  {(r.get('description') or '')[:80]}\")
"