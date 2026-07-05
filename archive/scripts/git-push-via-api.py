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
        # Convert date "2026-07-05T04:46:48Z" to git-format ("1783244808 +0000")
        def to_git_date(iso):
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            ts = int(dt.timestamp())
            # Git expects "Z" → "+0000"; explicit offset like "+08:00" → "+0800".
            if iso.endswith("Z"):
                tz = "+0000"
            else:
                # iso ends with "+HH:MM" or "-HH:MM"
                sign, hh, mm = iso[-6], iso[-5:-3], iso[-2:]
                tz = f"{sign}{hh}{mm}"
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


def find_unpushed_commits(local_repo, base_commit_local):
    """Return list of local commit SHAs between base_commit_local and HEAD
    (exclusive of base, inclusive of HEAD), in chronological order."""
    out = subprocess.run(
        ["git", "log", "--format=%H", f"{base_commit_local}~1..HEAD"],
        cwd=local_repo, capture_output=True, text=True, check=True,
    )
    return list(reversed([line for line in out.stdout.splitlines() if line.strip()]))


def push_single_commit(local, repo_owner, repo_name, commit_sha, remote_parent_sha,
                        token, branch="main", dry_run=False):
    """Post one local commit's contents through the GH DB API, with the new
    commit's parent set to remote_parent_sha on the GH side.

    `commit_sha` is the LOCAL commit we want to mirror; we extract its
    metadata + file diff using local objects, then create a GH-side
    commit whose parent matches the existing remote chain.
    """
    info = get_commit_info(local, commit_sha)
    message = get_commit_message(local, commit_sha)
    parent = get_parent_sha(local, commit_sha) or remote_parent_sha

    # 2. Find which files changed in this single commit
    diffs = diff_files(local, parent, commit_sha)
    print(f"[1/5] resolving base_tree from remote parent {remote_parent_sha[:8]}…",
          file=sys.stderr)
    base_tree = gh_get_tree_base(token, repo_owner, repo_name, remote_parent_sha)

    # 3. POST blobs for changes
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
            content = read_blob(local, commit_sha, path)
            blob_resp = gh_create_blob(token, repo_owner, repo_name, content)
            print(f"  {status} {path}: blob={blob_resp['sha'][:8]} ({len(content)}b)",
                  file=sys.stderr)
            tree_items.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_resp["sha"],
            })

    # 4. POST tree
    print(f"[3/5] posting tree (base_tree={base_tree[:8]})…", file=sys.stderr)
    new_tree = gh_create_tree(token, repo_owner, repo_name, tree_items,
                               base_tree_sha=base_tree)

    # 5. POST commit
    print(f"[4/5] posting commit (parent=remote {remote_parent_sha[:8]})…",
          file=sys.stderr)
    new_commit = gh_create_commit(token, repo_owner, repo_name, message, new_tree,
                                  remote_parent_sha, info, info)
    print(f"  new_commit={new_commit[:8]}", file=sys.stderr)

    # 6. PATCH ref
    print(f"[5/5] updating refs/heads/{branch}…", file=sys.stderr)
    if dry_run:
        print("DRY RUN — would PATCH refs", file=sys.stderr)
        return new_commit
    ref_resp = gh_update_ref(token, repo_owner, repo_name, branch,
                             new_commit, force=True)
    print(f"  ref now: {ref_resp['object']['sha'][:8]}", file=sys.stderr)
    return new_commit


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
    p.add_argument("--push-all-unpushed", action="store_true", help=(
        "Push every unpushed local commit (between origin/main and HEAD) "
        "as a separate GH-side commit, one per local commit. Each local "
        "commit's metadata + diff is mirrored exactly; SHA differs only "
        "due to the date-format SHA-algo divergence GitHub uses."
    ))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    owner, _, name = args.repo.partition("/")
    if not name:
        sys.exit("--repo must be owner/name")

    local = Path(args.local_repo).resolve()
    token = get_pat()

    if args.push_all_unpushed:
        # Resolve base commit (shared ancestor between local main and
        # remote main). Walk back from HEAD until we find a commit whose
        # SHA also exists on remote (= SHA unchanged).
        out = subprocess.run(
            ["git", "log", "--format=%H", "origin/main..HEAD"],
            cwd=local, capture_output=True, text=True, check=True,
        )
        unpushed_local = list(reversed([line for line in out.stdout.splitlines() if line.strip()]))
        if not unpushed_local:
            print("Nothing to push (origin/main already at HEAD).", file=sys.stderr)
            return

        # Find the LOCAL commit that immediately precedes the first
        # unpushed commit. That's our local-side base.
        first_unpushed = unpushed_local[0]
        local_base = get_parent_sha(local, first_unpushed)
        if not local_base:
            sys.exit("First unpushed commit has no parent — refusing to push")

        # The REMOTE-side base SHA either comes from --base-on-remote
        # (if provided) or from asking GH for the commit at that path.
        if args.base_on_remote:
            remote_base = args.base_on_remote
        else:
            # Try fetching the commit object's GH-side equivalent via
            # the GH API; if it returns the same SHA we already know the
            # remote mirror exists.
            try:
                resp = api("GET", f"https://api.github.com/repos/{owner}/{name}/git/commits/{local_base}",
                           token)
                remote_base = resp["sha"]
                if remote_base != local_base:
                    print(f"NOTE: GH SHA differs — local={local_base[:8]}, remote={remote_base[:8]}",
                          file=sys.stderr)
            except Exception as e:
                print(f"WARN: couldn't resolve remote equivalent of {local_base[:8]}: {e}",
                      file=sys.stderr)
                print("Pass --base-on-remote=<remote_sha> to skip the lookup.", file=sys.stderr)
                sys.exit(1)

        print(f"Pushing {len(unpushed_local)} unpushed commit(s) one-by-one "
              f"starting from remote base {remote_base[:8]}…", file=sys.stderr)
        current_remote_parent = remote_base
        for i, sha in enumerate(unpushed_local, 1):
            short = sha[:8]
            print(f"\n=== [{i}/{len(unpushed_local)}] local {short} ===", file=sys.stderr)
            current_remote_parent = push_single_commit(
                local, owner, name, sha, current_remote_parent,
                token, branch=args.branch, dry_run=args.dry_run,
            )
        print(f"\nDONE. {args.repo}@{args.branch} now at {current_remote_parent}",
              file=sys.stderr)
        return

    # Single-commit path (legacy behavior).
    new_sha = get_head_sha(local, args.branch)
    push_single_commit(local, owner, name, new_sha,
                       args.base_on_remote or get_parent_sha(local, new_sha),
                       token, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
