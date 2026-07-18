#!/usr/bin/env bash
# fetch_repo_profile.sh — 抓单仓的完整 profile（topics + meta + README + 任意文件）
# 用途：search 出候选后，抓完整数据验证「是不是真同类」
# 数据源：GitHub core API（不走 search rate limit，独立限速 60/h anonymous）
# 已知状况（2026-07-19 00:09 GMT+8）：
#   - GET /repos/:owner/:name → 200, 0.53s
#   - GET /repos/:owner/:name/readme → base64 content
#   - GET /repos/:owner/:name/contents/:path → 任意文件（绕 raw.githubusercontent.com timeout）
#   - GET /repos/:owner/:name/topics → topics array
# 局限：anonymous core API 60/h，1 仓全 profile = 4 calls = 15 仓/小时封顶
# 备注：raw.githubusercontent.com 偶发 15s timeout，core API /contents 路径更稳
set -euo pipefail

REPO="${1:?usage: fetch_repo_profile.sh owner/repo [extra_path]}"
EXTRA_PATH="${2:-}"

if [ -n "$EXTRA_PATH" ]; then
  curl -s "https://api.github.com/repos/${REPO}/contents/${EXTRA_PATH}" --max-time 15 \
    | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
if 'content' in d:
    print(base64.b64decode(d['content']).decode('utf-8', 'replace'))
else:
    print(json.dumps(d, indent=2))
"
  exit 0
fi

echo "=== meta ==="
curl -s "https://api.github.com/repos/${REPO}" --max-time 12 \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"stars={d.get('stargazers_count')} forks={d.get('forks_count')} lang={d.get('language')} pushed={d.get('pushed_at')}\")
print(f\"topics={d.get('topics')}\")
print(f\"desc={d.get('description')}\")
"

echo "=== README head ==="
curl -s "https://api.github.com/repos/${REPO}/readme" --max-time 12 \
  | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
content = base64.b64decode(d.get('content', '')).decode('utf-8', 'replace')
print(content[:2000])
"