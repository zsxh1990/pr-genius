#!/usr/bin/env python3
"""Migrate legacy v0.1 PR Case Study frontmatter to v0.5.0 schema.

Rules (matches ROUNDS_SCHEMA.md v0.5.0):
- action values get normalized to enum (verbatim) — anything with extra
  parenthetical text gets the parenthetical dropped
- delta values get reshaped from "string" to {kind: code_change/no_code_change/unknown, value: original_str_truncated}
- close_decision block gets appended at end of frontmatter (status: pending,
  reason: "auto-migrated from v0.1; pending close decision", actor: zsxh1990)
"""
import re
import sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/Eric Jia/research/big-repo-pr-knowledge")

ACTION_RE = re.compile(r'(?P<indent> +)action:\s*"(?P<v>[^"]+)"')
DELTA_STR_RE = re.compile(r'(?P<indent> +)delta:\s*"(?P<v>[^"]*)"')

# Action normalization map (legacy v0.1 -> v0.5.0 enum)
ACTION_MAP = {
    "open": "open",
    "open PR": "open",
    "amend": "amend",
    "amend (CLA + changeset)": "amend",
    "amend (bot findings)": "amend",
    "amend (CI fix: prettier)": "amend",
    "received maintainer feedback": "human_review",
    "third-party check-in": "check_in",
    "check_in": "check_in",
    "bot_review": "bot_review",
    "human_review": "human_review",
    "bump": "bump",
    "close": "close",
    "merge": "merge",
    "decision": "decision",
}

def delta_kind(value: str) -> str:
    """Heuristic: empty/未深读/no_code_change if v lacks code-meaningful info."""
    s = value.strip()
    if not s:
        return "unknown"
    lowered = s.lower()
    code_words = ("+", "/-", "/files", "files", "commit", "签", "加 ", "ship", "amend", "fix", "refactor", "patch")
    if any(w in s for w in code_words) or any(w in lowered for w in code_words):
        return "code_change"
    no_change_words = ("未深读", "未读", "未从", "no code", "unknown", "?", "n/a", "未追踪")
    if any(w in s for w in no_change_words):
        return "no_code_change"
    return "no_code_change"  # default cautious (round record without diff is "no diff observed")


def migrate_file(p: Path) -> tuple[bool, str]:
    text = p.read_text(encoding="utf-8")
    if "type: PR Case Study" not in text:
        return (False, "skip: not PR Case Study")
    if "close_decision:" in text:
        return (False, "skip: already migrated")

    changes = []

    # 1) normalize action
    def sub_action(m: re.Match) -> str:
        v = m.group("v")
        new_v = ACTION_MAP.get(v, v.split(" ")[0])  # fallback: first word
        if new_v != v:
            changes.append(f"action: {v!r} -> {new_v!r}")
        return f'{m.group("indent")}action: {new_v}'

    text2 = ACTION_RE.sub(sub_action, text)
    text = text2

    # 2) reshape delta (string -> object)
    def sub_delta(m: re.Match) -> str:
        indent = m.group("indent")
        v = m.group("v")
        kind = delta_kind(v)
        ev = v.replace('"', '\\"').replace("\n", " ")[:120]
        # The "indent" is the leading whitespace of `delta:` line itself; object fields
        # sit 2 columns deeper (rounds has 4-space indent, object sits at 6-space).
        # Determine proper sub-indent by counting depth of the parent key.
        # For YAML in this repo, rounds are at - 4 spaces ("    delta:" under "  - ..."), so object fields go 2 deeper.
        # But the captured indent already includes everything BEFORE delta:, which is
        # typically "    " for rounds. We'll add 2 more spaces for kind/value.
        sub = indent + "  "
        return f'{indent}delta:\n{sub}kind: {kind}\n{sub}value: "{ev}"'

    text2 = DELTA_STR_RE.sub(sub_delta, text)
    if text2 != text:
        # count delta conversions
        deltas_before = len(DELTA_STR_RE.findall(text))
        changes.append(f"delta: {deltas_before} entries -> object form")
        text = text2

    # 3) append close_decision block right before `final_status:` if present, else at end of frontmatter
    close_block = '''close_decision:
  status: pending
  reason: "auto-migrated from v0.1; pending close decision by zsxh1990"
  decided_at: null
  actor: zsxh1990
'''
    if "final_status:" in text:
        text = text.replace("final_status:", close_block + "final_status:", 1)
    else:
        # append before second `---` (end of frontmatter)
        fm_end = text.find("\n---", text.find("---", 3) + 3)
        if fm_end > 0:
            text = text[:fm_end] + "\n" + close_block + text[fm_end:]
        else:
            return (False, "skip: no fm_end")

    if not changes:
        return (False, "no_changes")

    p.write_text(text, encoding="utf-8")
    return (True, "; ".join(changes))


def main():
    targets = list(ROOT.glob("*-*/pr-[0-9]*.md"))
    print(f"scanning {len(targets)} PR Case Study files")
    total_changed = 0
    for p in sorted(targets):
        ok, msg = migrate_file(p)
        marker = "✓" if ok else "·"
        print(f"  {marker} {p.relative_to(ROOT)}: {msg}")
        if ok:
            total_changed += 1
    print(f"\ntotal changed: {total_changed}/{len(targets)}")


if __name__ == "__main__":
    main()
