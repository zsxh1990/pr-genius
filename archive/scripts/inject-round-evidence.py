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
    """Mutate file_path: add round-level fields to round 1 + amend rounds.

    Round 1 (open) gets HIGH-confidence evidence sourced from the GitHub
    PR's created_at + commits + files endpoints.

    Amend rounds (round >= 2 with action: amend, kind != no_code_change
    invariant) get LOW-confidence evidence using the round's existing
    `timestamp:` field as verified_at and the same PR files endpoint
    plus the PR API URL. We only target amend rounds whose delta.kind is
    "code_change" with value != null.
    """
    text = file_path.read_text(encoding="utf-8")
    fm_match = re.search(r"^repo:\s*(.+)$", text, re.MULTILINE)
    if not fm_match:
        return False, "no repo: in frontmatter"
    gh_repo = fm_match.group(1).strip()
    n_match = re.search(r"pr-(\d+)-", file_path.name)
    if not n_match:
        return False, "no pr-N- in filename"
    n = n_match.group(1)
    created_at = evidence["created_at"]
    head_short = evidence["head_short"]

    # Round 1 anchor: action: open, kind code_change or no_code_change
    open_pattern = re.compile(
        r"(    action: open\n    delta:\n      kind:\s*(?:code_change|no_code_change)\n      value:\s*\"[^\"]*\"(?:\s*#.*)?\n)"
    )
    m = open_pattern.search(text)
    injected_round1 = False
    # Idempotency: skip if next non-blank line is already `verified_at:`
    if m:
        already = re.search(r"      verified_at:", text[m.end():m.end()+80])
        if not already:
            add = (
                f"      verified_at: \"{created_at}\"\n"
                f"      evidence_urls:\n"
                f"        - https://github.com/{gh_repo}/pull/{n}/files\n"
                f"        - https://github.com/{gh_repo}/pull/{n}\n"
                f"        - https://api.github.com/repos/{gh_repo}/pulls/{n}/commits\n"
                f"      confidence: high  # PR created_at from GH API; commits at {head_short}\n"
            )
            text = text[: m.start()] + m.group(1) + add + text[m.end():]
            injected_round1 = True

    # Amend anchor: action: amend, kind code_change or no_code_change (kind != unknown)
    # OR kind: unknown but with explicit commit: <sha>.
    # Field order after value can vary; allow any number of indented
    # key:value / `- item` lines (separated by newlines) before
    # `    timestamp:` or `    commit:`.
    amend_anchor_code = re.compile(
        r"(    action: amend\n    delta:\n      kind:\s*(?:code_change|no_code_change)\n      value:\s*\"[^\"]*\"(?:\s*#.*)?\n(?:[ \t]+(?:- [^\n]*|[a-z_]+:[^\n]*)\n)+?    timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\")",
        re.MULTILINE,
    )
    amend_anchor_unknown_commit = re.compile(
        r"(    action: amend\n    delta:\n      kind:\s*unknown[^\n]*\n      value:[^\n]*\n(?:[ \t]+(?:- [^\n]*|[a-z_]+:[^\n]*)\n)+?    commit:\s*\"?([0-9a-f]{6,40})\"?\s*\n\s*timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\")",
        re.MULTILINE,
    )
    injected_amends = 0
    # Pass A: kind in {code_change, no_code_change}
    # Inject right after value: line so YAML indentation stays consistent
    # (verified_at / evidence_urls / confidence must be children of delta:).
    amend_anchor_code_inject = re.compile(
        r"(    action: amend\n    delta:\n      kind:\s*(?:code_change|no_code_change)\n      value:\s*\"[^\"]*\"(?:\s*#.*)?\n)([ \t]+)",
        re.MULTILINE,
    )
    for m in list(amend_anchor_code_inject.finditer(text)):
        # Check if this round already has round-level evidence
        post_value = text[m.end():m.end()+800]
        if re.search(r"\n      verified_at:", post_value):
            continue
        ts_iso_match = re.search(r"    timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\"", post_value)
        if not ts_iso_match:
            continue
        ts_iso = ts_iso_match.group(1)
        if ts_iso.endswith("T..."):
            ts_iso_full = ts_iso.replace("T...", "T00:00:00Z")
        else:
            ts_iso_full = ts_iso
        indent = m.group(2)
        # After `value: ...\n`, the next line is already a child of delta:
        # (at 6 spaces) or a sibling of delta: (at 4 spaces). Use indent as-is.
        add = (
            f"{indent}verified_at: \"{ts_iso_full}\"\n"
            f"{indent}evidence_urls:\n"
            f"{indent}  - https://github.com/{gh_repo}/pull/{n}\n"
            f"{indent}  - https://api.github.com/repos/{gh_repo}/pulls/{n}/files\n"
            f"{indent}confidence: low  # round-level timestamp from case body (not GH API cross-ref)\n"
        )
        # m.end(1) ends after group 1's `\n` so the splice keeps the next
        # line's indent intact (m.end() would consume indent = m.group(2)).
        text = text[: m.end(1)] + add + text[m.end(1):]
        injected_amends += 1

    # Pass B: kind: unknown but has explicit commit: <sha>
    # Same approach: inject right after value: line.
    amend_anchor_unknown_inject = re.compile(
        r"(    action: amend\n    delta:\n      kind:\s*unknown[^\n]*\n      value:[^\n]*\n)([ \t]+)",
        re.MULTILINE,
    )
    for m in list(amend_anchor_unknown_inject.finditer(text)):
        post_value = text[m.end():m.end()+800]
        if re.search(r"\n      verified_at:", post_value):
            continue
        sha_match = re.search(r"    commit:\s*\"?([0-9a-f]{6,40})\"?", post_value)
        ts_match = re.search(r"    timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\"", post_value)
        if not (sha_match and ts_match):
            continue
        sha = sha_match.group(1)
        ts_iso = ts_match.group(1)
        indent = m.group(2)
        add = (
            f"{indent}verified_at: \"{ts_iso}\"\n"
            f"{indent}evidence_urls:\n"
            f"{indent}  - https://github.com/{gh_repo}/pull/{n}/commits/{sha}\n"
            f"{indent}  - https://github.com/{gh_repo}/commit/{sha}\n"
            f"{indent}confidence: medium  # round-level commit SHA cross-refs to GH\n"
        )
        text = text[: m.end(1)] + add + text[m.end(1):]
        injected_amends += 1

    # Pass C: non-amend round WITH delta block (check_in / bump / bot_review /
    # merge / close / decision). Inject verified_at inside delta block.
    non_amend_anchor = re.compile(
        r"(    action:\s*(?:check_in|bump|bot_review|merge|close|decision)\n    delta:\n      kind:\s*(?:code_change|no_code_change)\n      value:[^\n]*\n)([ \t]+)",
        re.MULTILINE,
    )
    for m in list(non_amend_anchor.finditer(text)):
        post_value = text[m.end():m.end()+800]
        if re.search(r"\n      verified_at:", post_value):
            continue
        ts_match = re.search(r"    timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\"", post_value)
        if not ts_match:
            continue
        ts_iso = ts_match.group(1)
        indent = m.group(2)
        add = (
            f"{indent}verified_at: \"{ts_iso}\"\n"
            f"{indent}evidence_urls:\n"
            f"{indent}  - https://github.com/{gh_repo}/pull/{n}\n"
            f"{indent}  - https://api.github.com/repos/{gh_repo}/issues/{n}/comments\n"
            f"{indent}confidence: low  # round-level timestamp from case body (not GH API cross-ref)\n"
        )
        text = text[: m.end(1)] + add + text[m.end(1):]
        injected_amends += 1

    # Pass D: round WITHOUT delta: block (e.g. human_review where the case
    # body only records reviewer text). Inject verified_at as a sibling of
    # timestamp at round level (4-space indent).
    # Anchor: action line + 1..N sibling fields ending at timestamp.
    no_delta_anchor = re.compile(
        r"(    action:\s*(?:human_review|check_in|bump|bot_review|merge|close|decision)\n)(?:[ \t]+[a-z_]+:[^\n]*\n|[ \t]+- [^\n]*\n|[ \t]+\"[^\"]*\"\n)*[ \t]+timestamp:\s*\"(\d{4}-\d{2}-\d{2}T[^\"]*)\"",
        re.MULTILINE,
    )
    for m in list(no_delta_anchor.finditer(text)):
        post_value = text[m.end():m.end()+200]
        if re.search(r"^[ \t]+verified_at:", post_value, re.MULTILINE):
            continue
        # Verify this is a round block (preceded by `- round: N`)
        lookback = text[max(0, m.start()-80):m.start()]
        if not re.search(r"- round:\s*\d+\s*\n[ \t]+action:\s*", lookback):
            continue
        ts_iso = m.group(2)
        add = (
            f"    verified_at: \"{ts_iso}\"\n"
            f"    evidence_urls:\n"
            f"      - https://github.com/{gh_repo}/pull/{n}\n"
            f"      - https://api.github.com/repos/{gh_repo}/pulls/{n}/reviews\n"
            f"    confidence: low  # round-level timestamp from case body (not GH API cross-ref)\n"
        )
        # Insert immediately before `    timestamp:` line. m.end() is just
        # after timestamp ISO close quote.
        # Find the timestamp line start position within m.group(0).
        ts_line_pos = text.rfind("    timestamp:", m.start(), m.end())
        text = text[:ts_line_pos] + add + text[ts_line_pos:]
        injected_amends += 1

    if not (injected_round1 or injected_amends):
        return False, "no new anchors (already injected)"

    file_path.write_text(text, encoding="utf-8")
    parts = []
    if injected_round1:
        parts.append(f"round 1 ({head_short})")
    if injected_amends:
        parts.append(f"{injected_amends} amend round(s)")
    return True, "injected " + " + ".join(parts)


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
