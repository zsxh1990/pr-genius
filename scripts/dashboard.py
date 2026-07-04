"""pr-genius dashboard — open PR tracker.

Refactored: reads data/snapshot.json if present (emitted by validate.py --snapshot)
so the n-counts are not hand-written and won't drift.

Lists every tracked PR Case Study's final_status + days idle + relevant
fields, sorted by age descending.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUS_ORDER = {
    "pending": 0, "open": 1, "in-flight": 1,
    "merged": 2, "closed": 3, "superseded": 4, "keep_open": 1,
}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r'---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = line.split(':', 1)
        if len(kv) == 2:
            key = kv[0].strip()
            val = kv[1].strip().strip('"').strip("'")
            fm[key] = val
    return fm


def gather_case_studies() -> list:
    rows = []
    for path in ROOT.rglob("pr-*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if fm.get('type') != 'PR Case Study':
            continue
        fs = fm.get('final_status', 'unknown')
        ts_list = re.findall(r'timestamp:\s*["\']?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', text)
        latest_ts = max(ts_list) if ts_list else None
        rows.append({
            'folder': path.parent.name,
            'name': path.name,
            'pr_number': fm.get('pr_number', '?'),
            'pr_url': fm.get('pr_url', ''),
            'repo': fm.get('repo', path.parent.name),
            'final_status': fs,
            'status_label': STATUS_ORDER.get(fs, 9),
            'latest_round_ts': latest_ts,
            'opened_at': fm.get('opened_at', '') or fm.get('merged_at', ''),
            'schema_version': fm.get('schema_version', 'legacy v0.1'),
            'close_decision_status': _extract_close_decision(text),
        })
    return rows


def _extract_close_decision(text: str) -> str | None:
    m = re.search(r'close_decision:\s*\n\s*status:\s*(\S+)', text)
    return m.group(1) if m else None


def compute_days_idle(rows: list) -> list:
    now = datetime.now(timezone.utc)
    for r in rows:
        ts_str = r.get('latest_round_ts')
        if ts_str:
            try:
                clean = ts_str.rstrip('Z').rstrip('"').rstrip("'")
                dt = datetime.fromisoformat(clean)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                r['days_idle'] = (now - dt).days
                r['last_activity'] = dt.isoformat()
            except (ValueError, TypeError):
                r['days_idle'] = None
                r['last_activity'] = ts_str
        else:
            r['days_idle'] = None
            r['last_activity'] = None
    return rows


def load_snapshot():
    """If validate.py --snapshot has been run, return its n-counts."""
    p = ROOT / "data" / "snapshot.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def render_table(rows: list, only_stale: bool = False) -> str:
    rows = [r for r in rows if r['final_status'] in ('open', 'in-flight', 'pending')]
    if only_stale:
        rows = [r for r in rows if r.get('days_idle') is not None and r['days_idle'] >= 14]
    rows.sort(key=lambda r: (r.get('days_idle') or -1), reverse=True)
    out = ['# Open PR Case Studies\n']
    out.append(f"Total open: {len(rows)}\n")
    if not rows:
        return '\n'.join(out)
    out.append('| Days idle | Repo | PR | Status | Last activity | Decision |')
    out.append('|---|---|---|---|---|---|')
    for r in rows:
        didle = r.get('days_idle')
        didle_str = f"{didle}d" if didle is not None else '—'
        last = (r.get('last_activity') or '—')[:10]
        cd = r.get('close_decision_status') or '—'
        pr_url = r['pr_url'] or f"#{r['pr_number']}"
        repo_short = r['repo'].split('/')[-1] if '/' in r['repo'] else r['repo']
        out.append(f"| {didle_str} | {repo_short} | [#{r['pr_number']}]({pr_url}) | {r['final_status']} | {last} | {cd} |")
    return '\n'.join(out)


def main():
    rows = gather_case_studies()
    rows = compute_days_idle(rows)
    if '--json' in sys.argv:
        # also include snapshot n-counts if available
        out = {"snapshot": load_snapshot(), "rows": rows}
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    only_stale = '--stale' in sys.argv
    print(render_table(rows, only_stale))
    print()
    all_open = [r for r in rows if r['final_status'] in ('open', 'in-flight', 'pending')]
    idle_14d = [r for r in all_open if r.get('days_idle') is not None and r['days_idle'] >= 14]
    idle_30d = [r for r in all_open if r.get('days_idle') is not None and r['days_idle'] >= 30]
    snap = load_snapshot()
    snap_str = ""
    if snap:
        snap_str = f" (snapshot: {snap['profiles']} profiles / {snap['case_studies']} cases)"
    print(f"> stale (≥14d open): {len(idle_14d)}/{len(all_open)}")
    print(f"> stale (≥30d open): {len(idle_30d)}/{len(all_open)}")
    print(f"> all open {len(all_open)}, all cases {len(rows)} total{snap_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
