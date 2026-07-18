#!/usr/bin/env bash
# search_pr_coach.sh — 搜 PR coach / advisor / analyzer 类仓
# 用途：找「PR 提交前自检」工具，跟 pr-genius 同赛道
# 数据源：GitHub 匿名 search API（限速 10/min）
# 已知状态（2026-07-18 23:55 GMT+8）：
#   - 命中 6496 个 total
#   - top: 0xarchit/github-profile-analyzer(855) — 非同类（分析用户主页）
#   - 半同类: hancengiz/claude-code-prompt-coach-skill(147)
set -euo pipefail

QUERY='%22PR+coach%22+OR+%22PR+advisor%22+OR+%22contribution+advisor%22+OR+%22PR+analyzer%22+OR+%22contribution+coach%22'
PER_PAGE="${PER_PAGE:-15}"

curl -s "https://api.github.com/search/repositories?q=${QUERY}&sort=stars&order=desc&per_page=${PER_PAGE}" \
  --max-time 15 | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"total={d.get('total_count', 0)}\")
for r in d.get('items', []):
    print(f\"⭐{r['stargazers_count']:>6}  {r['full_name']:50}  {(r.get('description') or '')[:80]}\")
"