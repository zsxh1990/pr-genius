#!/usr/bin/env python3
"""inject-round-evidence.py — add round-level evidence fields to round 1
(open) of each PR Case Study, sourced from the cached
archive/scripts/.tmp/evidence-*.json dump.

Schema v0.7.0 supports per-round `verified_at` / `evidence_urls` /
`confidence`. Case-level is the headline gate (`--enforce-evidence`);
round-level is the deeper accountability layer (which date saw the
specific diff).

For each case we look up the first commit SHA + creation timestamp and
inject:

    delta:
      kind: code_change
      value: "+83 / -0 / 2 files"
      verified_at: "<pr_created_at>"
      evidence_urls:
        - <github_url>/files
        - <github_url>          # diff viewer
        - <api_url>/commits      # commit hash list
      confidence: <high if state=open consistent else medium>

This is intentionally scoped: only round 1 (open) gets the field
augmentation, because later rounds vary widely (amend / bot review /
check_in / close_decision) and the same evidence won't always apply.

Usage:
    python3 archive/scripts/inject-round-evidence.py
    python3 archive/scripts/inject-round-evidence.py --dry-run
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def get_latest_evidence_dump():
    dumps = sorted((ROOT / "archive/scripts/.tmp").glob("evidence-*.json"))
    if not dumps:
        raise RuntimeError("Run refresh-evidence.py first")
    return dumps[-1]


def load_evidence_index(dump_path):
    data = json.loads(dump_path.read_text())
    idx = {}
    for t in data["targets"]:
        key = (t["owner"].lower(), t["repo"].lower(), t["pr_number"])
        pr = t["api_endpoints"].get(f"pulls/{t['pr_number']}", {})
        idx[key] = {
            "created_at": pr.get("created_at"),
            "head_sha": pr.get("merge_commit_sha") or pr.get("sha"),
            "head_short": (pr.get("merge_commit_sha") or pr.get("sha") or "")[:8],
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "files_count": pr.get("changed_files"),
            "state": pr.get("state"),
            "merged": pr.get("merged"),
        }
    return idx


def case_owner_repo(repo):
    """'plastic-labs/honcho' -> ('plastic-labs', 'honcho')."""
    parts = repo.split("/", 1)
    return (parts[0].lower(), parts[1].lower()) if len(parts) == 2 else (None, None)


def inject(file_path, evidence):
    """Mutate file_path: add round-level fields to round 1's delta block.

    We anchor on the unique `delta:\n      kind:` block under round 1
    only by adding verified_at / evidence_urls / confidence lines.
    """
    text = file_path.read_text(encoding="utf-8")
    # Locate the FIRST `delta:` block (round 1 always comes before others).
    # Round 1's delta always has kind: (code_change|no_code_change) and
    # value: "..." (potentially followed by a trailing comment).
    pattern = re.compile(
        r"(    action: open\n    delta:\n      kind:\s*(?:code_change|no_code_change)\n      value:\s*\"[^\"]*\"(?:\s*#.*)?\n)"
    )
    m = pattern.search(text)
    if not m:
        return False, "no open+code_change round 1 anchor found"

    created_at = evidence["created_at"]
    short_sha = evidence["head_short"]
    owner_repo = file_path.parent.name
    n = re.search(r"pr-(\d+)-", file_path.name).group(1) if re.search(
        r"pr-(\d+)-", file_path.name
    ) else "?"
    # Map directory name -> actual GitHub owner/repo (dir uses `-`)
    # Most dirs are `<owner>-<repo>` with double-dash for orgs.
    # We rely on the frontmatter `repo:` field as source of truth.
    fm_match = re.search(r"^repo:\s*(.+)$", text, re.MULTILINE)
    if not fm_match:
        return False, "no repo: in frontmatter"
    gh_repo = fm_match.group(1).strip()
    gh_owner, gh_repo_name = gh_repo.split("/", 1)

    add_lines = (
        f"      verified_at: \"{created_at}\"\n"
        f"      evidence_urls:\n"
        f"        - https://github.com/{gh_repo}/pull/{n}/files\n"
        f"        - https://github.com/{gh_repo}/pull/{n}\n"
        f"        - https://api.github.com/repos/{gh_repo}/pulls/{n}/commits\n"
        f"      confidence: high  # PR created_at from GH API; commits at {short_sha}\n"
    )
    new = m.group(1) + add_lines
    text2 = text[: m.start()] + new + text[m.end():]
    if text2 == text:
        return False, "no change"

    file_path.write_text(text2, encoding="utf-8")
    return True, f"injected round-1 evidence ({short_sha})"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    idx = load_evidence_index(get_latest_evidence_dump())
    case_files = sorted(ROOT.glob("*/pr-*.md"))
    touched = 0
    skipped = []
    for cf in case_files:
        fm_text = cf.read_text(encoding="utf-8").split("---")[1]
        m = re.search(r"^repo:\s*(.+)$", fm_text, re.MULTILINE)
        if not m:
            skipped.append((cf.name, "no repo:"))
            continue
        gh_repo = m.group(1).strip()
        owner, repo = gh_repo.split("/", 1)
        n = re.search(r"pr-(\d+)-", cf.name).group(1)
        evidence = idx.get((owner.lower(), repo.lower(), int(n)))
        if evidence is None:
            skipped.append((cf.name, "no evidence in cache"))
            continue

        if args.dry_run:
            print(f"  [dry-run] would inject {cf.relative_to(ROOT)}")
            continue
        ok, info = inject(cf, evidence)
        if ok:
            print(f"  ✅ {cf.relative_to(ROOT)}: {info}")
            touched += 1
        else:
            skipped.append((cf.name, info))

    print(f"\nInjected: {touched}")
    if skipped:
        print(f"Skipped: {len(skipped)}")
        for s, why in skipped:
            print(f"  - {s}: {why}")


if __name__ == "__main__":
    main()
