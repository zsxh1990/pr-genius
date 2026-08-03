#!/usr/bin/env bash
# pr_status_heartbeat.sh — Outbound PR status heartbeat
#
# Wraps `prgenius status` for daily cron. Outputs human-readable summary
# and saves JSON snapshot to data/snapshots/.
#
# Usage:
#   bash scripts/pr_status_heartbeat.sh                    # default: zsxh1990
#   bash scripts/pr_status_heartbeat.sh --author zsxh1990  # explicit author
#   bash scripts/pr_status_heartbeat.sh --author Ikalus1988
#   bash scripts/pr_status_heartbeat.sh --all              # both accounts
#
# Exit codes:
#   0 = no action needed (all green)
#   1 = actionable items found (rebase/CI/ping)
#   2 = script error
#
# Cron example (daily 10:00 Asia/Shanghai):
#   0 10 * * * cd /path/to/pr-genius && bash scripts/pr_status_heartbeat.sh --all
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SNAPSHOT_DIR="${REPO_ROOT}/data/snapshots"
PRGENIUS_SRC="${REPO_ROOT}/prgenius/src"
mkdir -p "$SNAPSHOT_DIR"

# Use local source, not installed PyPI package
export PYTHONPATH="${PRGENIUS_SRC}:${PYTHONPATH:-}"

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

AUTHORS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --author) AUTHORS+=("$2"); shift 2 ;;
        --all)    AUTHORS=("zsxh1990" "Ikalus1988"); shift ;;
        *)        echo "Unknown arg: $1"; exit 2 ;;
    esac
done
[[ ${#AUTHORS[@]} -eq 0 ]] && AUTHORS=("zsxh1990")

HAS_ACTION=0

for AUTHOR in "${AUTHORS[@]}"; do
    echo "═══════════════════════════════════════════════════"
    echo "  PR Genius Status — ${AUTHOR} (${DATE})"
    echo "═══════════════════════════════════════════════════"
    echo ""

    # Human-readable table output
    python3 -m prgenius status --author "$AUTHOR" --format table 2>&1 || {
        echo "ERROR: prgenius status failed for ${AUTHOR}" >&2
        continue
    }
    echo ""

    # JSON snapshot
    SNAPSHOT_FILE="${SNAPSHOT_DIR}/${AUTHOR}_${DATE}.json"
    JSON_OUTPUT=$(python3 -m prgenius status --author "$AUTHOR" --format json --save-snapshot 2>&1) || true

    if [[ -n "$JSON_OUTPUT" ]]; then
        echo "$JSON_OUTPUT" > "$SNAPSHOT_FILE"

        # Check for actionable items
        ACTION_COUNT=$(echo "$JSON_OUTPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    actionable = sum(1 for p in data.get('prs', [])
                     if p.get('status') in ('NEEDS_REBASE', 'CI_FAILING', 'STALE_REVIEW', 'STALE_NO_REVIEW'))
    print(actionable)
except:
    print(0)
" 2>/dev/null || echo "0")

        if [[ "$ACTION_COUNT" -gt 0 ]]; then
            HAS_ACTION=1
            echo "⚡ ${ACTION_COUNT} actionable item(s) for ${AUTHOR}"
        fi

        echo "📸 Snapshot: ${SNAPSHOT_FILE}"
    fi
    echo ""
done

echo "───────────────────────────────────────────────────"
echo "  Heartbeat complete at ${TIMESTAMP}"
echo "───────────────────────────────────────────────────"

exit $HAS_ACTION
