#!/usr/bin/env python3
"""refresh-evidence.py - fetch GH API evidence for N=5 PR case studies.

N1 self-decision: read GH API endpoints for these PRs and dump structured
evidence (commits / files / reviews / comments / PR-meta) to a tmp JSON.
The next pass (separate script or manual edit) inserts case-level
frontmatter fields (verified_at / evidence_urls / confidence) into the
corresponding pr-N-*.md files.

Usage:
    python3 archive/scripts/refresh-evidence.py

Reads:
    ~/.git-credentials (zsxh1990 PAT line)
Writes:
    archive/scripts/.tmp/evidence-YYYYMMDD-HHMMSS.json  (gitignored)

Per-PR endpoints (5):
    /repos/{owner}/{repo}/pulls/{n}
    /repos/{owner}/{repo}/pulls/{n}/files
    /repos/{owner}/{repo}/issues/{n}/comments
    /repos/{owner}/{repo}/pulls/{n}/reviews
    /repos/{owner}/{repo}/pulls/{n}/commits

Rate limit: PAT is fine-grained; 5*5=25 calls fits easily.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

# Targets (N1 self-decision: 5 PRs covering schema diversity)
TARGETS = [
    ("plastic-labs", "honcho", 801),
    ("qdrant", "mcp-server-qdrant", 143),
    ("astral-sh", "uv", 19685),
    ("mongodb-js", "mongodb-mcp-server", 1309),
    ("agentic-community", "mcp-gateway-registry", 1382),
    # Phase 2 (r0.7.2): cover remaining 6 --enforce-evidence gaps
    ("e2b-dev", "E2B", 1413),
    ("future-agi", "future-agi", 778),
    ("harbor-framework", "harbor", 2121),
    ("punkpeye", "fastmcp", 282),
    ("agentic-community", "mcp-gateway-registry", 1383),
    ("sourcebot-dev", "sourcebot", 1383),
]	

# GH API endpoints we want per PR
ENDPOINTS = [
    "pulls/{n}",          # PR meta (state / merged / merged_at / merge_commit_sha / user)
    "pulls/{n}/files",    # files + add/del lines
    "issues/{n}/comments",  # all comment objects (created_at / user / body)
    "pulls/{n}/reviews",  # review events (state + submitted_at + user)
    "pulls/{n}/commits",  # commit SHAs
]

API = "https://api.github.com"


def load_pat():
    creds = Path.home() / ".git-credentials"
    for line in creds.read_text().splitlines():
        if line.startswith("https://zsxh1990:"):
            # https://zsxh1990:TOKEN@github.com
            after_scheme = line[len("https://"):]
            _, _, token_at_host = after_scheme.partition("@")
            # Actually the format is "https://USER:TOKEN@HOST"
            user, _, rest = line[len("https://"):].rpartition("@")
            user, _, token = user.partition(":")
            if user == "zsxh1990":
                return token
            # Fallback: try simpler parsing
    raise RuntimeError("zsxh1990 PAT not found in ~/.git-credentials")


def fetch(url, token, retries=3):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_err


def main():
    token = load_pat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(__file__).parent / ".tmp"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"evidence-{stamp}.json"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets": [],
        "rate_limit_remaining": None,
    }
    for owner, repo, n in TARGETS:
        entry = {
            "owner": owner,
            "repo": repo,
            "pr_number": n,
            "api_endpoints": {},
            "errors": [],
        }
        for ep_pattern in ENDPOINTS:
            ep = ep_pattern.format(n=n)
            url = f"{API}/repos/{owner}/{repo}/{ep}"
            try:
                data = fetch(url, token)
                # Strip very long bodies to keep cache small
                if ep == "issues/{n}/comments" or ep.endswith("/comments"):
                    data = [
                        {k: v for k, v in c.items() if k not in ("body_html",)}
                        for c in data
                    ]
                    # Truncate body to 240 chars (we want timestamps, not full text)
                    for c in data:
                        if "body" in c and isinstance(c["body"], str):
                            c["body_preview"] = c["body"][:240]
                            del c["body"]
                if ep == "pulls/{n}/files":
                    # drop `patch` field (huge); keep filename + add/del/status
                    entry["api_endpoints"][ep] = [
                        {
                            "filename": f.get("filename"),
                            "status": f.get("status"),
                            "additions": f.get("additions"),
                            "deletions": f.get("deletions"),
                            "changes": f.get("changes"),
                        }
                        for f in data
                    ]
                else:
                    # keep timestamp + state + user only for compactness
                    if isinstance(data, list):
                        compact = []
                        for x in data:
                            keep = {
                                k: v for k, v in x.items()
                                if k in (
                                    "id", "state", "created_at", "submitted_at",
                                    "updated_at", "merged_at", "closed_at",
                                    "commit_id", "sha", "user", "title",
                                    "author_association",
                                )
                            }
                            compact.append(keep)
                        entry["api_endpoints"][ep] = compact
                    else:
                        keep = {
                            k: v for k, v in data.items()
                            if k in (
                                "id", "number", "state", "title", "user",
                                "created_at", "updated_at", "closed_at",
                                "merged", "merged_at", "merged_by",
                                "merge_commit_sha", "additions", "deletions",
                                "changed_files", "comments", "review_comments",
                                "commits", "author_association",
                                "labels", "draft",
                            )
                        }
                        entry["api_endpoints"][ep] = keep
            except Exception as e:
                entry["errors"].append({"endpoint": ep, "error": str(e)})
        report["targets"].append(entry)
        # gentle pacing to avoid burst-rate
        time.sleep(1)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"WROTE {out_path} ({out_path.stat().st_size} bytes)", file=sys.stderr)
    # summary
    ok = sum(1 for t in report["targets"] if not t["errors"])
    print(f"OK {ok}/{len(TARGETS)} PRs.", file=sys.stderr)
    for t in report["targets"]:
        if t["errors"]:
            print(f"  ERR {t['owner']}/{t['repo']}#{t['pr_number']}: "
                  f"{len(t['errors'])} endpoint(s) failed", file=sys.stderr)


if __name__ == "__main__":
    main()
