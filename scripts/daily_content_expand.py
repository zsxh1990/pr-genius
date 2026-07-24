#!/usr/bin/env python3
"""PR Genius Daily Content Expansion — Heartbeat Task.

Samples 50 PRs from large/medium repos, analyzes quality patterns,
and creates case studies for the PR knowledge base.

Quality diversity targets:
  - 15 merged (success patterns)
  - 15 closed-without-merge (anti-patterns)
  - 10 with substantive review comments (learning)
  - 10 from first-time contributors (onboarding patterns)

Repo diversity targets:
  - Mix of languages (Python, TS, Go, Rust, etc.)
  - Mix of project types (infra, AI/ML, devtools, web)
  - Star range: 1k - 100k+

Usage:
    python3 scripts/daily_content_expand.py
    python3 scripts/daily_content_expand.py --dry-run
    python3 scripts/daily_content_expand.py --limit 20
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ── Target repos: large/medium OSS projects ──

TARGET_REPOS = [
    # AI/ML
    "langchain-ai/langchain",
    "langchain-ai/langgraph",
    "microsoft/markitdown",
    "huggingface/transformers",
    "openai/openai-python",
    "anthropics/anthropic-sdk-python",
    "modelcontextprotocol/python-sdk",
    # DevTools
    "astral-sh/uv",
    "astral-sh/ruff",
    "vercel/next.js",
    "microsoft/TypeScript",
    "facebook/react",
    "tailwindlabs/tailwindcss",
    # Infra/Cloud
    "kubernetes/kubernetes",
    "grafana/grafana",
    "goharbor/harbor",
    "prometheus/prometheus",
    "hashicorp/terraform",
    # Python ecosystem
    "psf/requests",
    "pallets/flask",
    "encode/httpx",
    "pydantic/pydantic",
    "fastapi/fastapi",
    # Rust/Go
    "rust-lang/rust",
    "denoland/deno",
    "golang/go",
    # DevOps
    "cli/cli",
    "docker/compose",
    "actions/checkout",
    # Data
    "qdrant/qdrant",
    "mongodb/mongo-python-driver",
    "chroma-core/chroma",
    "electron/electron",
]


def _run_gh(args: list[str], timeout: int = 30) -> dict | list | None:
    """Run gh CLI and return JSON result."""
    cmd = ["gh"] + args + ["--json", "number,title,state,mergedAt,closedAt,author,createdAt,additions,deletions,changedFiles,reviews,comments,labels"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _fetch_recent_prs(repo: str, state: str = "all", limit: int = 10) -> list[dict]:
    """Fetch recent PRs from a repo using gh pr list."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--state", state,
             "--limit", str(limit), "--json",
             "number,title,state,mergedAt,closedAt,author,createdAt,additions,deletions,changedFiles,reviews,comments,labels,updatedAt"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            prs = json.loads(result.stdout)
            # Add repo field
            for pr in prs:
                pr["_repo"] = repo
            return prs
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def _classify_pr(pr: dict) -> str:
    """Classify PR into quality category."""
    state = pr.get("state", "").lower()
    merged = pr.get("mergedAt") is not None  # gh pr list uses camelCase
    reviews = pr.get("reviews", [])
    comments = pr.get("comments", [])

    if merged:
        return "merged_success"
    elif state == "closed":
        comment_bodies = " ".join((c.get("body", "") or "").lower() for c in comments)
        if "duplicate" in comment_bodies:
            return "closed_duplicate"
        elif "already" in comment_bodies or "superseded" in comment_bodies:
            return "closed_already_done"
        else:
            return "closed_rejected"
    elif len(reviews) > 0:
        has_critical = any(
            (r.get("state", "") or "").lower() in ("changes_requested", "dismissed")
            for r in reviews
        )
        if has_critical:
            return "review_changes_requested"
        else:
            return "review_approved_pending"
    else:
        return "open_pending"


def _extract_signals(pr: dict, repo: str) -> dict:
    """Extract learning signals from a PR.

    Includes both text-based signals (from title/body) and metadata-based
    signals (from PR stats) to avoid all-False cases for bot PRs.
    """
    body = pr.get("body", "") or ""
    title = pr.get("title", "") or ""
    title_lower = title.lower()
    body_lower = body.lower()

    files = pr.get("changedFiles", 0)
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    total_changes = additions + deletions

    signals = {
        # Text-based signals
        "has_issue_link": "fixes #" in body_lower or "closes #" in body_lower or "fixes https://" in body_lower,
        "has_description": len(body) > 100,
        "has_test_mention": any(w in body_lower for w in ["test", "spec", "coverage"]),
        "has_breaking_change": any(w in title_lower for w in ["breaking", "major", "v2"]),
        "is_docs_only": any(w in title_lower for w in ["docs", "readme", "documentation", ".md"]),
        "is_bug_fix": any(w in title_lower for w in ["fix", "bug", "patch", "hotfix"]),
        "is_feature": any(w in title_lower for w in ["feat", "feature", "add", "support"]),
        "is_refactor": any(w in title_lower for w in ["refactor", "clean", "chore", "perf"]),
        # Metadata-based signals (always have value)
        "is_small_pr": files <= 3 and total_changes < 50,
        "is_large_pr": files > 10 or total_changes > 500,
        "is_backport": "backport" in title_lower or "release" in title_lower,
        "is_dependency_update": any(w in title_lower for w in ["bump", "update", "upgrade", "dependabot"]),
        "is_bot_pr": any(w in title_lower for w in ["dependabot", "renovate", "bot", "auto-", "[ci"]),
        "has_reviews": len(pr.get("reviews", [])) > 0,
        "has_comments": len(pr.get("comments", [])) > 0,
        # Numeric metrics
        "files_changed": files,
        "additions": additions,
        "deletions": deletions,
        "review_count": len(pr.get("reviews", [])),
        "comment_count": len(pr.get("comments", [])),
        "change_ratio": round(deletions / max(additions, 1), 2),  # >1 = net deletion
    }

    return signals


def _create_case_study(pr: dict, repo: str, category: str, signals: dict) -> dict:
    """Create a structured case study from a PR."""
    author = pr.get("author", {})
    if isinstance(author, dict):
        author_login = author.get("login", "unknown")
    else:
        author_login = str(author)

    return {
        "id": f"{repo.replace('/', '-')}-{pr['number']}",
        "repo": repo,
        "pr_number": pr["number"],
        "title": pr.get("title", ""),
        "author": author_login,
        "state": pr.get("state", ""),
        "merged": pr.get("mergedAt") is not None,
        "category": category,
        "created_at": pr.get("createdAt", ""),
        "signals": signals,
        "metrics": {
            "files_changed": pr.get("changedFiles", 0),
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
        },
    }


def _save_case_study(case: dict):
    """Save case study to appropriate directory."""
    category = case["category"]

    if category.startswith("merged"):
        out_dir = REPO / "success-patterns"
    elif category.startswith("closed"):
        out_dir = REPO / "anti-patterns"
    else:
        out_dir = REPO / "review-cases"

    out_dir.mkdir(exist_ok=True)

    filename = f"{case['id']}.json"
    out_path = out_dir / filename

    # Don't overwrite existing
    if out_path.exists():
        return False

    out_path.write_text(json.dumps(case, indent=2, ensure_ascii=False))
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    limit = 50
    for i, arg in enumerate(sys.argv):
        if arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    print(f"PR Genius Daily Content Expansion")
    print(f"Target: {limit} PRs from {len(TARGET_REPOS)} repos")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()[:19]}")
    print()

    # Category quotas
    quotas = {
        "merged_success": 15,
        "closed_rejected": 8,
        "closed_duplicate": 4,
        "closed_already_done": 3,
        "review_changes_requested": 5,
        "review_approved_pending": 5,
        "open_pending": 10,
    }

    collected: dict[str, list] = {k: [] for k in quotas}
    total_fetched = 0
    new_cases = 0
    skipped_repos = []

    # Shuffle repos for variety
    import random
    repos = TARGET_REPOS.copy()
    random.shuffle(repos)

    for repo in repos:
        # Check if all quotas are met
        if all(len(collected[k]) >= v for k, v in quotas.items()):
            break

        total_needed = sum(
            max(0, quotas[k] - len(collected[k]))
            for k in quotas
        )
        if total_needed == 0:
            break

        print(f"  📦 {repo}...", end=" ", flush=True)
        prs = _fetch_recent_prs(repo, state="all", limit=15)
        total_fetched += len(prs)

        if not prs:
            print("skip (no data)")
            skipped_repos.append(repo)
            continue

        repo_new = 0
        for pr in prs:
            category = _classify_pr(pr)

            # Check quota
            if len(collected[category]) >= quotas.get(category, 0):
                continue

            # Skip if we already have this PR
            pr_id = f"{repo.replace('/', '-')}-{pr['number']}"
            if any(c["id"] == pr_id for c_collected in collected.values() for c in c_collected):
                continue

            signals = _extract_signals(pr, repo)
            case = _create_case_study(pr, repo, category, signals)

            if not dry_run:
                if _save_case_study(case):
                    new_cases += 1
                    repo_new += 1

            collected[category].append(case)

        total_collected = sum(len(v) for v in collected.values())
        print(f"+{repo_new} (total: {total_collected}/{limit})")
        time.sleep(0.5)  # Rate limiting

    # Summary
    print(f"\n{'='*60}")
    print(f"Daily Expansion Summary")
    print(f"{'='*60}")
    print(f"Repos scanned: {len(repos) - len(skipped_repos)}/{len(repos)}")
    print(f"PRs fetched: {total_fetched}")
    print(f"New cases: {new_cases}")
    print()

    for cat, items in sorted(collected.items()):
        quota = quotas[cat]
        status = "✅" if len(items) >= quota else "⚠️"
        print(f"  {status} {cat:30s} {len(items):>3}/{quota}")

    if skipped_repos:
        print(f"\nSkipped repos: {', '.join(skipped_repos[:5])}")

    # Save daily report
    report = {
        "date": datetime.now(timezone.utc).isoformat()[:10],
        "repos_scanned": len(repos) - len(skipped_repos),
        "prs_fetched": total_fetched,
        "new_cases": new_cases,
        "category_counts": {k: len(v) for k, v in collected.items()},
        "skipped_repos": skipped_repos,
    }

    report_path = REPO / "docs" / "daily_expansion_report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
