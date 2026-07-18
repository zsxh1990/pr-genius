#!/usr/bin/env bash
# search_good_first_issue.sh — 搜 good-first-issue / first contribution 类仓
# 用途：找「教人提第一个 PR」的仓（first-contributions 同类）
# 数据源：GitHub 匿名 search API（限速 10/min；该 query 撞过 reset 后才出结果）
# 已知状态（2026-07-19 00:01 GMT+8）：
#   - 撞 rate limit 时返 0；sleep 30 + 重试后才出 total=3013
#   - top: firstcontributions/first-contributions(55k) — **真同类**（但只教 git 流程）
#   - 大部分 top 结果噪声（terminal/file manager/CRM）
# 备注：anonymous search 限速 10/min；如果一次返 0 立刻 sleep 30 重试
set -euo pipefail

QUERY='good-first-issue'
PER_PAGE="${PER_PAGE:-15}"
RETRY="${RETRY:-1}"
RETRY_SLEEP="${RETRY_SLEEP:-30}"

run_search() {
  curl -s "https://api.github.com/search/repositories?q=${QUERY}&sort=stars&order=desc&per_page=${PER_PAGE}" \
    --max-time 15 | python3 -c "
import sys, json
d = json.load(sys.stdin)
items = d.get('items')
if items is None:
    print(f\"ERR: {d.get('message', 'no items, possibly rate-limited')}\")
    sys.exit(2)
print(f\"total={d['total_count']}\")
for r in items:
    print(f\"⭐{r['stargazers_count']:>6}  {r['full_name']:50}  {(r.get('description') or '')[:80]}\")
"
}

if run_search && [ "$RETRY" = "1" ]; then
  exit 0
fi

echo "rate-limited, sleep ${RETRY_SLEEP}s and retry..."
sleep "$RETRY_SLEEP"
run_search