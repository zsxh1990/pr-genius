#!/usr/bin/env bash
# search_okf_bundle.sh — 搜 OKF / agent-first markdown knowledge bundle 类仓
# 用途：找跟 pr-genius 同形（agent-first markdown knowledge system）的仓
# 数据源：GitHub 匿名 search API
# 已知状态（2026-07-18 23:55 GMT+8）：
#   - 命中 2402 个 total
#   - top: outline/outline(40k, 团队 wiki)、quarkdown(16k, markdown 超集)、
#           agenticnotetaking/arscontexta(3.4k, **真同形** — Claude Code 知识系统插件)、
#           1st1/lat.md(1.8k, **真同形** — codebase knowledge graph in markdown)
set -euo pipefail

QUERY='%22open+knowledge+format%22+OR+OKF+bundle+OR+%22agent+readable%22+markdown+knowledge'
PER_PAGE="${PER_PAGE:-15}"

curl -s "https://api.github.com/search/repositories?q=${QUERY}&sort=stars&order=desc&per_page=${PER_PAGE}" \
  --max-time 15 | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"total={d.get('total_count', 0)}\")
for r in d.get('items', []):
    print(f\"⭐{r['stargazers_count']:>6}  {r['full_name']:50}  {(r.get('description') or '')[:80]}\")
"