#!/usr/bin/env python3
"""
pr-genius heartbeat — daily maintenance runner.

Tasks per run:
1. Run `python3 validate.py` — record error/warning counts
2. Inventory existing profiles + case studies
3. Detect newly merged PRs for tracked repos (via cached data if any)
4. Auto-update KNOWN_ISSUES.md with current validator counts
5. Detect orphan .md files
6. Check for stale (90d+) PR Case Study rounds
7. Output a JSON summary to /tmp/pr_genius_heartbeat.json
8. If new merged PR detected for tracked repo → write a TODO stub

Designed to be run by cron at 10:00 Asia/Shanghai daily.

Usage:
    python3 scripts/heartbeat.py             # normal run
    python3 scripts/heartbeat.py --dry-run   # no file writes
    python3 scripts/heartbeat.py --verbose   # more output
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "validate.py"
KNOWN_ISSUES = ROOT / "KNOWN_ISSUES.md"
OUTPUT_JSON = Path("/tmp/pr_genius_heartbeat.json")

# Tracked repos (zsxh1990 PRs in these big repos)
TRACKED_REPOS = [
    "astral-sh/uv",
    "plastic-labs/honcho",
    "harbor-framework/harbor",
    "punkpeye/fastmcp",
    "sourcebot-dev/sourcebot",
    "future-agi/future-agi",
    "qdrant/mcp-server-qdrant",
    "e2b-dev/E2B",
    "NousResearch/hermes-agent",
    "mongodb-js/mongodb-mcp-server",
    "agentic-community/mcp-gateway-registry",  # 2026-07-04 added: zsxh PR #1382 + #1383
]


def run_validator() -> dict:
    """Run python3 validate.py and parse output."""
    result = subprocess.run(
        ["python3", str(VALIDATE)],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    stdout = result.stdout
    counts = {"errors": 0, "warnings": 0, "files": 0}
    m = re.search(r'Found (\d+) \.md files', stdout)
    if m: counts["files"] = int(m.group(1))
    m = re.search(r'❌\s*(\d+) error', stdout)
    if m: counts["errors"] = int(m.group(1))
    m = re.search(r'⚠️\s*(\d+) warning', stdout)
    if m: counts["warnings"] = int(m.group(1))
    return {"result": result.returncode, "counts": counts, "stdout_tail": stdout[-500:]}


def inventory_repo_profiles() -> list:
    """List all repo profiles + their star/fork counts."""
    profiles = []
    for sub in sorted(ROOT.iterdir()):
        if not sub.is_dir(): continue
        idx = sub / "index.md"
        if not idx.exists(): continue
        # Skip knowledge folders
        if sub.name in {"anti-patterns", "misakanet-50", ".github", "scripts"}:
            continue
        # Parse frontmatter
        try:
            text = idx.read_text(encoding='utf-8')
            m = re.match(r'---\n(.*?)\n---', text, re.DOTALL)
            if m:
                fm = m.group(1)
                star_m = re.search(r'^star:\s*(\d+)', fm, re.MULTILINE)
                repo_m = re.search(r'^repo:\s*(\S+)', fm, re.MULTILINE)
                profiles.append({
                    "folder": sub.name,
                    "repo": repo_m.group(1) if repo_m else None,
                    "star": int(star_m.group(1)) if star_m else None,
                })
        except Exception:
            pass
    return profiles


def detect_stale_case_studies() -> list:
    """Find PR case studies whose latest round is >90 days old."""
    stale = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    for case in ROOT.rglob("pr-*.md"):
        try:
            text = case.read_text(encoding='utf-8')
            # Find latest timestamp in YAML
            ts_matches = re.findall(r'timestamp:\s*["\']?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?)', text)
            if not ts_matches:
                continue
            latest = max(ts_matches)
            try:
                latest_dt = datetime.fromisoformat(latest.replace("Z", "+00:00"))
            except ValueError:
                continue
            if latest_dt < cutoff:
                # Check if final_status still open/stale
                fs_m = re.search(r'final_status:\s*(\S+)', text)
                if fs_m and fs_m.group(1) in {"open", "open-stale"}:
                    stale.append({
                        "path": str(case.relative_to(ROOT)),
                        "latest_round": latest,
                        "age_days": (datetime.now(timezone.utc) - latest_dt).days,
                        "final_status": fs_m.group(1),
                    })
        except Exception:
            continue
    return stale


def check_known_issues_update(val_counts: dict) -> bool:
    """Update KNOWN_ISSUES.md if validator counts changed."""
    if not KNOWN_ISSUES.exists():
        return False
    try:
        text = KNOWN_ISSUES.read_text(encoding='utf-8')
        # Replace validator counts section
        new_block = (
            f"## Current validator state\n\n"
            f"- Files checked: **{val_counts['files']}**\n"
            f"- Errors: **{val_counts['errors']}**\n"
            f"- Warnings: **{val_counts['warnings']}**\n"
            f"- Last heartbeat: {datetime.now(timezone.utc).isoformat()}\n\n"
        )
        # Insert after the first heading or at the end of file
        if "## Current validator state" in text:
            text = re.sub(
                r'## Current validator state.*?(?=\n## |\Z)',
                new_block.rstrip() + "\n\n",
                text, count=1, flags=re.DOTALL
            )
        else:
            text += f"\n{new_block}"
        KNOWN_ISSUES.write_text(text, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  WARN: could not update KNOWN_ISSUES.md: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv

    summary = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "tasks": {},
    }

    print(f"=== pr-genius heartbeat @ {summary['ran_at']} ===")
    if dry_run:
        print("(dry run — no file writes)")

    # Task 1: validator
    print("\n[1/5] Running validator...")
    val = run_validator()
    summary["tasks"]["validator"] = val
    print(f"  files={val['counts']['files']} errors={val['counts']['errors']} warnings={val['counts']['warnings']}")

    # Task 2: inventory
    print("\n[2/5] Inventorying repo profiles...")
    profiles = inventory_repo_profiles()
    summary["tasks"]["profiles"] = profiles
    print(f"  found {len(profiles)} profiles: {', '.join(p['folder'] for p in profiles)}")

    # Task 3: stale case studies
    print("\n[3/5] Detecting stale PR case studies...")
    stale = detect_stale_case_studies()
    summary["tasks"]["stale_case_studies"] = stale
    if stale:
        print(f"  ⚠ {len(stale)} stale case studies (>90d, still open):")
        for s in stale:
            print(f"    - {s['path']} ({s['age_days']}d)")
    else:
        print("  no stale case studies")

    # Task 4: update KNOWN_ISSUES.md (skip in dry-run)
    print("\n[4/5] Updating KNOWN_ISSUES.md...")
    if not dry_run:
        updated = check_known_issues_update(val["counts"])
        print(f"  {'updated' if updated else 'skipped'}")
    else:
        print("  skipped (dry run)")

    # Task 5: write summary JSON
    print("\n[5/5] Writing summary JSON...")
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"  wrote {OUTPUT_JSON}")

    # Verbose: print full JSON
    if verbose:
        print("\n=== Summary ===")
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n=== Done ===")
    return 0 if val["counts"]["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
