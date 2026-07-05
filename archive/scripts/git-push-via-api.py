#!/usr/bin/env python3
"""git-push-via-api.py — Workaround for WSL→github.com:443 dead route.

Pushes one commit to a GitHub repo using the Git Database API
(api.github.com, which is on a working route) instead of the regular
git+https protocol (which goes via github.com:443, currently dead).

This is meant as an emergency workaround, NOT a replacement for
`git push`. Use only when:
  - `git push` times out on the github.com handshake
  - You can reach api.github.com but not github.com (today's situation)
  - You need to ship a single commit

Usage:
    python3 /tmp/git-push-via-api.py \
        --repo zsxh1990/pr-genius \
        --local-repo /mnt/c/Users/Eric\\ Jia/research/big-repo-pr-knowledge \
        --branch main
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def get_pat():
    creds = Path.home() / ".git-credentials"
    for line in creds.read_text().splitlines():
        if not line.startswith("https://"):
            continue
        user, _, rest = line[len("https://"):].rpartition("@")
        u, _, t = user.partition(":")
        if u == "zsxh1990":
            return t
    raise RuntimeError("zsxh1990 PAT not in ~/.git-credentials")


def _get_token_quietly():
    try:
        return get_pat()
    except Exception:
        return None


def _infer_owner_repo(local_repo):
    """Best-effort: read origin URL and parse owner/name."""
    out = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=local_repo, capture_output=True, text=True,
    )
    if out.returncode != 0:
        return (None, None)
    url = out.stdout.strip()
    if url.startswith("https://"):
        path = url[len("https://"):].rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        # Two shapes:
        #   https://github.com/owner/name           (no auth in URL)
        #   https://USER:TOKEN@github.com/owner/name (auth baked in)
        if "@" in path:
            _, _, host_path = path.partition("@")
        else:
            host_path = path
        _, _, repo_part = host_path.partition("/")
        if not repo_part:
            return (None, None)
        owner, _, name = repo_part.partition("/")
        return (owner, name)
    return (None, None)


def _fetch_remote_commit_to_local(token, owner, name, sha, local_repo):
    """Fetch a single commit object from GitHub API into the local git
    object database. Handles --base-on-remote pointing to a commit
    that was pushed via Git-DB-API and so isn't reachable from local refs.
    """
    from datetime import datetime
    pending = [sha]
    seen = set()
    while pending:
        cur = pending.pop()
        if cur in seen:
            continue
        seen.add(cur)
        out = api("GET",
                  f"https://api.github.com/repos/{owner}/{name}/git/commits/{cur}",
                  token)
        parents = out.get("parents", [])
        tree_sha = out["tree"]["sha"]
        author = out["author"]
        committer = out["committer"]
        message = out["message"]
        # Convert date "2026-07-05T04:46:48Z" to "1783244808 +0800"
        def to_git_date(iso):
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            ts = int(dt.timestamp())
            tz = iso[-5:]  # "+0800" or "+0000"
            return (ts, tz)
        a_ts, a_tz = to_git_date(author["date"])
        c_ts, c_tz = to_git_date(committer["date"])
        parents_str = "".join(f"parent {p['sha']}\n" for p in parents)
        commit_obj = (
            f"tree {tree_sha}\n"
            f"{parents_str}"
            f"author {author['name']} <{author['email']}> {a_ts} {a_tz}\n"
            f"committer {committer['name']} <{committer['email']}> {c_ts} {c_tz}\n"
            f"\n{message}\n"
        )
        subprocess.run(
            ["git", "hash-object", "-t", "commit", "-w", "--stdin"],
            cwd=local_repo, input=commit_obj.encode("utf-8"),
            capture_output=True, check=True,
        )
        pending.append(tree_sha)
        pending.extend(p["sha"] for p in parents)


def api(method, url, token, body=None, accept="application/vnd.github+json"):
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            req.add_header("Content-Type", "application/json")
        elif isinstance(body, bytes):
            data = body
        else:
            data = str(body).encode("utf-8")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, data=data, timeout=30) as resp:
                raw = resp.read()
                if not raw:
                    return {}
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"{method} {url} -> {e.code}: {err}") from None


def get_head_sha(local_repo, branch):
    out = subprocess.run(
        ["git", "rev-parse", branch],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def get_parent_sha(local_repo, commit_sha):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%P", commit_sha],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    parents = out.stdout.strip().split()
    return parents[0] if parents else None


def get_commit_subject(local_repo, commit_sha):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%s", commit_sha],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def get_commit_message(local_repo, commit_sha):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%B", commit_sha],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def _normalize_date(iso_with_tz):
    """git log %ai/%ci returns '2026-07-05 11:18:32 +0800' — GH API wants ISO-8601 with :HH:MM offset."""
    # '2026-07-05 11:25:31 +0800' → '2026-07-05T11:25:31+08:00'
    date_part, _, tz_part = iso_with_tz.rpartition(" ")
    if "+" in tz_part or "-" in tz_part[1:]:
        sign = tz_part[0]
        body = tz_part[1:]
        if len(body) == 4:
            tz_part = f"{sign}{body[:2]}:{body[2:]}"
    return f"{date_part.replace(' ', 'T')}{tz_part}"


def get_commit_info(local_repo, commit_sha):
    """Return dict with author_name, author_email, author_date (ISO normalized), committer_name, committer_email, committer_date (ISO normalized)."""
    fmt = "%an%n%ae%n%ai%n%cn%n%ce%n%ci"
    out = subprocess.run(
        ["git", "log", "-1", f"--format={fmt}", commit_sha],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    lines = out.stdout.rstrip("\n").split("\n")
    if len(lines) < 6:
        raise RuntimeError(f"git log format wrong: {lines}")
    return {
        "author_name": lines[0],
        "author_email": lines[1],
        "author_date": _normalize_date(lines[2]),
        "committer_name": lines[3],
        "committer_email": lines[4],
        "committer_date": _normalize_date(lines[5]),
    }


def diff_files(local_repo, base_sha, head_sha):
    """Return list of (status, path) tuples — empty for merges by design.

    If base_sha isn't in the local object database (common with GH-DB-API
    pushed commits whose SHA differs from local), fetch it via the
    GitHub API before diffing.
    """
    try:
        subprocess.run(
            ["git", "cat-file", "-t", base_sha],
            cwd=local_repo, capture_output=True, text=True, check=False,
        )
    except subprocess.CalledProcessError:
        owner, name = _infer_owner_repo(local_repo)
        token = _get_token_quietly()
        if owner and token:
            _fetch_remote_commit_to_local(token, owner, name, base_sha, local_repo)
        else:
            raise

    # Check whether object actually exists now (or after fetch).
    check = subprocess.run(
        ["git", "cat-file", "-t", base_sha],
        cwd=local_repo, capture_output=True, text=True,
    )
    if check.returncode != 0:
        owner, name = _infer_owner_repo(local_repo)
        token = _get_token_quietly()
        if owner and token:
            _fetch_remote_commit_to_local(token, owner, name, base_sha, local_repo)
        else:
            raise RuntimeError(f"base commit {base_sha} not in local objects")
    out = subprocess.run(
        ["git", "diff", "--name-status", base_sha, head_sha],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    files = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            # R100\told\tnew or C75\told\tnew
            path = parts[2]
        else:
            path = parts[1]
        files.append((status, path))
    return files


def get_blob_sha(local_repo, commit_sha, path):
    out = subprocess.run(
        ["git", "ls-tree", commit_sha, "--", path],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "blob":
            return parts[2], int(parts[3] if len(parts) > 3 else "100644", 8)
    return None


def read_blob(local_repo, commit_sha, path):
    out = subprocess.run(
        ["git", "show", f"{commit_sha}:{path}"],
        cwd=local_repo, capture_output=True, check=True,
    )
    return out.stdout


def gh_create_blob(token, owner, repo, content_bytes):
    # base64 encode — GitHub blob API supports utf-8 or base64
    encoded = base64.b64encode(content_bytes).decode("ascii")
    return api("POST",
               f"https://api.github.com/repos/{owner}/{repo}/git/blobs",
               token,
               body={"content": encoded, "encoding": "base64"})


def gh_get_tree_base(token, owner, repo, base_commit_sha, recursive=False):
    # GitHub lets you POST a tree with base_tree=<sha> and only modified entries —
    # it preserves unchanged blobs from the base. This is the fast path.
    out = api("GET",
              f"https://api.github.com/repos/{owner}/{repo}/git/commits/{base_commit_sha}",
              token)
    return out["tree"]["sha"]


def gh_create_tree(token, owner, repo, items, base_tree_sha=None):
    body = {"tree": items}
    if base_tree_sha:
        body["base_tree"] = base_tree_sha
    return api("POST",
               f"https://api.github.com/repos/{owner}/{repo}/git/trees",
               token,
               body=body)["sha"]


def gh_create_commit(token, owner, repo, message, tree_sha, parent_sha,
                     author, committer):
    body = {
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha] if parent_sha else [],
        "author": {
            "name": author["author_name"],
            "email": author["author_email"],
            "date": author["author_date"],
        },
        "committer": {
            "name": committer["committer_name"],
            "email": committer["committer_email"],
            "date": committer["committer_date"],
        },
    }
    return api("POST",
               f"https://api.github.com/repos/{owner}/{repo}/git/commits",
               token,
               body=body)["sha"]


def gh_update_ref(token, owner, repo, branch, new_sha, force=True):
    body = {"sha": new_sha, "force": force}
    return api("PATCH",
               f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
               token,
               body=body)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--local-repo", required=True)
    p.add_argument("--branch", default="main")
    p.add_argument("--base-on-remote", help=(
        "If local parent SHA doesn't exist on remote (common in this WSL "
        "workaround where GH API generates different SHAs than local git "
        "due to date-format differences), pass the remote-side parent SHA "
        "here. The script will use its tree as the base_tree."
    ))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    owner, _, name = args.repo.partition("/")
    if not name:
        sys.exit("--repo must be owner/name")

    local = Path(args.local_repo).resolve()
    token = get_pat()

    # 1. Compute what's about to land
    new_sha = get_head_sha(local, args.branch)
    info = get_commit_info(local, new_sha)
    message = get_commit_message(local, new_sha)

    # If --base-on-remote given, diff against that and squash all
    # unpushed commits into one big push commit. Otherwise, push only the
    # latest commit (parent = HEAD~1).
    if args.base_on_remote:
        parent = args.base_on_remote
    else:
        parent = get_parent_sha(local, new_sha)
        if not parent:
            sys.exit("First commit (no parent) — too risky for one-shot fallback")

    # 2. Find which files changed (vs parent)
    diffs = diff_files(local, parent, new_sha)
    if any(s.startswith(("A", "M", "D", "T", "R", "C")) for s, _ in diffs):
        pass  # any of these are fine

    # 3. Get base_tree from parent's commit on the remote side.
    # If local parent SHA isn't on remote, fall back to --base-on-remote.
    remote_parent_sha = args.base_on_remote or parent
    print(f"[1/5] resolving base_tree from remote parent {remote_parent_sha[:8]}…",
          file=sys.stderr)
    base_tree = gh_get_tree_base(token, owner, name, remote_parent_sha)

    # 4. For each changed file, create a new blob and add to tree
    print(f"[2/5] posting blobs for {len(diffs)} changed file(s)…",
          file=sys.stderr)
    tree_items = []
    for status, path in diffs:
        if status == "D":
            tree_items.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": None,
            })
        else:
            content = read_blob(local, new_sha, path)
            blob_resp = gh_create_blob(token, owner, name, content)
            print(f"  {status} {path}: blob={blob_resp['sha'][:8]} ({len(content)}b)",
                  file=sys.stderr)
            tree_items.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_resp["sha"],
            })

    # 5. POST new tree with base_tree=base_tree (preserves unchanged)
    print(f"[3/5] posting tree (base_tree={base_tree[:8]})…", file=sys.stderr)
    new_tree = gh_create_tree(token, owner, name, tree_items, base_tree_sha=base_tree)

    # 6. POST new commit pointing at new_tree, parent=remote_parent_sha
    # (use the remote parent so GH lineage is intact).
    print(f"[4/5] posting commit…", file=sys.stderr)
    new_commit = gh_create_commit(token, owner, name, message, new_tree,
                                  remote_parent_sha, info, info)
    print(f"  new_commit={new_commit[:8]}", file=sys.stderr)

    # 7. PATCH refs/heads/<branch>
    print(f"[5/5] updating refs/heads/{args.branch}…", file=sys.stderr)
    if args.dry_run:
        print("DRY RUN — would PATCH refs", file=sys.stderr)
        return
    ref_resp = gh_update_ref(token, owner, name, args.branch, new_commit,
                             force=True)
    print(f"  ref now: {ref_resp['object']['sha'][:8]}", file=sys.stderr)

    print(f"\nDONE. {args.repo}@{args.branch} now at {new_commit}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
