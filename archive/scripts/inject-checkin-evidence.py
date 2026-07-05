#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path("/mnt/c/Users/Eric Jia/research/big-repo-pr-knowledge")
TARGETS = [
    ("astral-sh-uv/pr-19685-sarif-audit.md", 2, 19685, "astral-sh/uv", "human_review"),
    ("future-agi-future-agi/pr-778-span-list-without-project-id.md", 3, 778, "future-agi/future-agi", "check_in"),
    ("plastic-labs-honcho/pr-801-queue-purge.md", 4, 801, "plastic-labs/honcho", "check_in"),
    ("qdrant-mcp-server-qdrant/pr-143-ollama-provider.md", 3, 143, "qdrant/mcp-server-qdrant", "bump"),
]

for relpath, round_num, pr_n, gh_repo, action in TARGETS:
    f = ROOT / relpath
    text = f.read_text(encoding="utf-8")
    # Anchor on `- round: N\n    action: <action>\n    delta:\n      kind: <kind>\n      value: <value>\n`
    # then INSERT immediately after, with 6-space indent (children of delta).
    pat = re.compile(
        rf"(- round:\s*{round_num}\n    action:\s*{action}\n    delta:\n      kind:\s*\w+\n      value:[^\n]*\n)",
        re.MULTILINE,
    )
    m = pat.search(text)
    if not m:
        print(f"  ❌ {relpath} round {round_num}: no anchor")
        continue
    # Look ahead to find timestamp within the round (skip over delta children + sibling fields)
    rest = text[m.end():]
    ts_match = re.search(r"^    timestamp:\s*\"([^\"]+)\"", rest, re.MULTILINE)
    if not ts_match:
        print(f"  ❌ {relpath} round {round_num}: no timestamp in rest")
        continue
    ts_iso = ts_match.group(1)
    if ts_iso.endswith("T..."):
        ts_iso = ts_iso.replace("T...", "T00:00:00Z")
    if "verified_at" in text[m.start():m.end()+200]:
        print(f"  ⏭ {relpath} round {round_num}: already has evidence")
        continue
    add = (
        f"      verified_at: \"{ts_iso}\"\n"
        f"      evidence_urls:\n"
        f"        - https://github.com/{gh_repo}/pull/{pr_n}\n"
        f"        - https://api.github.com/repos/{gh_repo}/issues/{pr_n}/comments\n"
        f"      confidence: low  # no_code_change round — verified via timestamp + comments URL\n"
    )
    text = text[: m.end()] + add + text[m.end():]
    f.write_text(text, encoding="utf-8")
    print(f"  ✅ {relpath} round {round_num}: injected ts={ts_iso}")
