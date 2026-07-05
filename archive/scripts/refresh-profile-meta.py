#!/usr/bin/env python3
"""refresh-profile-meta.py — fetch GH API repo metadata + inject into
profile `index.md` frontmatter as `verified_at / evidence_urls / confidence
/ last_release / last_commit_sha`.

Adds 3 (optionally 4) new fields to existing frontmatter:

  verified_at: "<ISO timestamp>"            # when this script ran
  evidence_urls:                             # 4 GH-side URLs cross-ref-ing
    - https://github.com/<owner>/<name>             # human
    - https://api.github.com/repos/<owner>/<name>  # API
    - https://api.github.com/repos/.../releases/latest
    - https://api.github.com/repos/.../commits?per_page=1
  confidence: high  # autogen from GH API; placeholder until human-curated

Idempotent: if `verified_at` already exists in the frontmatter, the
profile is skipped.

Usage:
    python3 archive/scripts/refresh-profile-meta.py [--dry-run]
"""
import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def get_pat():
    line = Path.home().joinpath(".git-credentials").read_text().splitlines()
    for raw in line:
        if not raw.startswith("https://"):
            continue
        user_part, _, rest = raw[len("https://"):].rpartition("@")
        u, _, t = user_part.partition(":")
        if u == "zsxh1990":
            return t
    raise RuntimeError("no zsxh1990 PAT")


def api(method, url, token):
    req = urllib.request.Request(
        url, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8", errors="replace")[:200]}


def fetch_profile_meta(token, owner, repo_name):
    """Return dict with star / fork / last_release / last_commit_sha."""
    meta = {"owner": owner, "name": repo_name}

    # Repo meta
    status, data = api("GET",
        f"https://api.github.com/repos/{owner}/{repo_name}", token)
    if status == 200:
        meta.update({
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "language": data.get("language"),
            "size_kb": data.get("size"),
            "license": data.get("license", {}).get("spdx_id") if isinstance(data.get("license"), dict) else None,
            "open_issues": data.get("open_issues_count"),
            "default_branch": data.get("default_branch"),
            "gh_url": data.get("html_url"),
            "archived": data.get("archived"),
            "last_pushed_at": data.get("pushed_at"),
        })

    # Latest release
    status, rel = api("GET",
        f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest", token)
    if status == 200:
        meta["last_release"] = rel.get("tag_name")
        meta["last_release_at"] = rel.get("published_at")
        meta["last_release_url"] = rel.get("html_url")
    else:
        meta["last_release"] = None

    # Last commit
    status, commits = api("GET",
        f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1",
        token)
    if status == 200 and commits:
        meta["last_commit_sha"] = commits[0].get("sha", "")[:8]
        meta["last_commit_at"] = commits[0].get("commit", {}).get("author", {}).get("date")

    return meta


def iter_profile_dirs():
    excluded = {"docs", "archive", "scripts", "misakanet-50", "prgenius",
                "anti-patterns", "data", ".github"}
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and d.name not in excluded and (d / "index.md").exists():
            yield d


def extract_repo_from_frontmatter(text):
    fm = text.split("---", 2)[1] if "---" in text else ""
    # Look for `gh_repo: <owner>/<name>` line
    m = re.search(r"^gh_repo:\s*[\"']?([^\"'\s#]+/[^\"'\s#]+)",
                  fm, re.MULTILINE)
    if m:
        return m.group(1)
    # Fallback: title hint or `repo:` field
    m2 = re.search(r"^repo:\s*[\"']?([^\"'\s#]+/[^\"'\s#]+)",
                   fm, re.MULTILINE)
    if m2:
        return m2.group(1)
    return None


def upsert_profile_meta(index_path, meta, dry_run):
    text = index_path.read_text(encoding="utf-8")
    # Find the second `---` (closing frontmatter).
    if not text.startswith("---"):
        return False, "no frontmatter (missing opening ---)"
    rest = text[3:]
    # rest starts with content; first \n---\n is fm-closing.
    sep = "\n---"
    if sep not in rest:
        return False, "no frontmatter (no closing ---)"
    fm, body = rest.split(sep, 1)
    # fm is the YAML; body starts with possible leading newline then markdown.

    # Already has verified_at? Idempotent skip.
    if re.search(r"^verified_at:", fm, re.MULTILINE):
        return False, "already filled"

    # Build insert block
    owner = meta["owner"]
    name = meta["name"]
    lines = [
        f"verified_at: \"{meta.get('fetched_at', '')}\"",
        "evidence_urls:",
        f"  - https://github.com/{owner}/{name}",
        f"  - https://api.github.com/repos/{owner}/{name}",
        f"  - https://api.github.com/repos/{owner}/{name}/releases/latest",
        f"  - https://api.github.com/repos/{owner}/{name}/commits",
        "confidence: high  # autogen from GH API; bump to medium if human-curated",
    ]
    if meta.get("last_release"):
        lines.append(f"last_release: {meta['last_release']}")
    if meta.get("last_commit_sha"):
        lines.append(f"last_commit_sha: {meta['last_commit_sha']}")
    if meta.get("stars") is not None:
        lines.append(f"stars: {meta['stars']}")

    new_fm = fm.rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    if body.startswith("\n"):
        new_body = "\n" + body
    else:
        new_body = "\n\n" + body
    new_text = "---" + new_fm + "---" + new_body
    if new_text == text:
        return False, "no-op"

    if dry_run:
        return True, "DRY RUN — would append"
    index_path.write_text(new_text, encoding="utf-8")
    return True, "appended"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    token = get_pat()
    from datetime import datetime, timezone
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    ok = skipped = 0
    for prof_dir in iter_profile_dirs():
        index_file = prof_dir / "index.md"
        text = index_file.read_text(encoding="utf-8")
        repo = extract_repo_from_frontmatter(text)
        if not repo:
            print(f"  skip {prof_dir.name}: no gh_repo/repo in frontmatter",
                  flush=True)
            skipped += 1
            continue
        owner, _, name = repo.partition("/")

        meta = fetch_profile_meta(token, owner, name)
        meta["fetched_at"] = fetched_at
        if meta.get("stars") is None:
            print(f"  SKIP {prof_dir.name}: GH API returned no data for {repo}",
                  flush=True)
            skipped += 1
            continue

        edited, info = upsert_profile_meta(index_file, meta, dry_run=args.dry_run)
        if edited:
            print(f"  ✅ {prof_dir.name} ({repo}): {info} — ⭐{meta.get('stars')}",
                  flush=True)
            ok += 1
        else:
            print(f"  -- {prof_dir.name} ({repo}): {info}", flush=True)
            skipped += 1

    print(f"\nUpdated: {ok}, Skipped: {skipped}", flush=True)


if __name__ == "__main__":
    main()