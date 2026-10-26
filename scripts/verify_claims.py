#!/usr/bin/env python3
"""Verify that README / CHANGELOG / docs claims match the live repo.

Audit E.6: three releases in a row shipped with claims that didn't survive
empirical inspection (v2.1.0 retracted two, v2.1.4 had to verify the gate,
v2.2.x had to revise maturity assessment). This script re-measures every
count claim the docs make, diffs against the live tree, and exits non-zero
on drift.

Run from repo root:
    python3 scripts/verify_claims.py

Returns exit 0 if all claims hold; exit 1 if any drift is detected.

Scope (intentionally narrow — added one claim at a time as drift surfaced):

  1. README.md: "943 loaded patterns across 67 repos" (pre-29268b2) OR
                "753 loaded patterns across 67 repos, plus 190 PR observations"
                (post-29268b2) — see `ALLOWED_PATTERNS` below.
  2. README.md: 14 MCP tools table (analyze_pr / coach_pr / triage_pr / ...)
  3. prgenius/src/prgenius/__init__.py __version__ aligned with
     prgenius/pyproject.toml version.
  4. CHANGELOG.md top entry must match the aligned version.

What this script does NOT do (yet):

  * It does not check the maturity self-assessment numbers (form
    completeness / engineering convergence / equal-weighted %). Those
    require human judgment about what counts.
  * It does not check that the README "943 patterns" claim against the
    pre-29268b2 corpus — it only allows the *current* claim format
    (`ALLOWED_PATTERNS` lists both pre- and post-refactor phrasings).
  * It does not verify MCP tool count by actually running the server.
    That belongs in `prgenius doctor`.

If a new claim type starts drifting, add it to the `CLAIMS` list. Keep
the regex narrow enough that a rephrasing without a real change still
passes — false positives erode trust faster than the drift itself.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _live_anti_patterns() -> tuple[int, int, int]:
    """Return (total, md, json) for anti-patterns/*. Counts what the
    loader would count — not just glob counts, because the README splits
    md from json differently depending on whether 29268b2 has landed."""
    anti_dir = REPO_ROOT / "anti-patterns"
    md = sum(1 for p in anti_dir.glob("*.md") if p.name != "README.md")
    json_ = sum(1 for p in anti_dir.glob("*.json"))
    return md + json_, md, json_


def _live_success_patterns() -> int:
    return sum(1 for p in (REPO_ROOT / "success-patterns").glob("*.md") if p.name != "README.md") + \
           sum(1 for p in (REPO_ROOT / "success-patterns").glob("*.json"))


def _live_count(dirname: str, pattern: str) -> int:
    d = REPO_ROOT / dirname
    return sum(1 for _ in d.glob(pattern)) if d.is_dir() else 0


def _live_mcp_tools() -> list[str]:
    """Parse the `@mcp.tool(` decorators in prgenius/src/prgenius/mcp.py.
    Avoids importing mcp (which is an optional extra) and avoids running
    the server."""
    text = _read("prgenius/src/prgenius/mcp.py")
    return re.findall(r"@mcp\.tool\(", text)


def _live_init_version() -> str:
    text = _read("prgenius/src/prgenius/__init__.py")
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else ""


def _live_pyproject_version() -> str:
    text = _read("prgenius/pyproject.toml")
    m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    return m.group(1) if m else ""


def _live_contract_gate_count() -> int:
    """Run the DSH plugin contract gate and parse its blocking-check count.

    Why the gate has to measure this rather than trust a literal: the count moves
    whenever checks are added or retired (#117 took it 27 -> 29, #131 trimmed it
    back), and the docs kept saying 27/27 in three places — including an expected
    output line inside a block titled "可复跑" (#136). A hardcoded number in prose
    is a claim with no writer; this makes the gate the one that notices.
    """
    script = REPO_ROOT / "scripts" / "check_dsh_plugin_contract.py"
    if not script.exists():
        return -1
    try:
        out = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
        )
    except Exception:
        return -1
    m = re.search(r"(\d+)\s*/\s*\d+\s+blocking checks passed", out.stdout + out.stderr)
    return int(m.group(1)) if m else -1


_CONTRACT_CLAIM = re.compile(r"(\d+)\s*/\s*\d+\s+blocking checks")
_CONTRACT_CLAIM_CN = re.compile(r"契约符合性[^\d]{0,20}(\d+)\s*/\s*\d+")


def _doc_contract_claims() -> list[tuple[str, int]]:
    """Every place a document states a blocking-check count, as (where, claimed)."""
    found: list[tuple[str, int]] = []
    for rel in ("README.md", "docs/maturity-self-assessment.md"):
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for rx in (_CONTRACT_CLAIM, _CONTRACT_CLAIM_CN):
                m = rx.search(line)
                if m:
                    found.append((f"{rel}:{lineno}", int(m.group(1))))
    return found



def _slot_catalog_alignment() -> tuple[bool, str]:
    """Run scripts/verify-slot-keys.mjs and report whether the catalog snapshot
    matches its own authority (#139).

    It was failing on main for weeks while every release still tagged: a gate
    nobody runs is not a gate. This makes a stale snapshot refuse the release the
    same way a version mismatch does.
    """
    script = REPO_ROOT / "scripts" / "verify-slot-keys.mjs"
    if not script.exists():
        return False, "scripts/verify-slot-keys.mjs is missing"
    try:
        out = subprocess.run(
            ["node", str(script), "--check"],
            capture_output=True, text=True, timeout=180, cwd=str(REPO_ROOT),
        )
    except Exception as exc:  # noqa: BLE001 - the message is the product here
        return False, f"could not run verify-slot-keys.mjs: {exc}"
    text = out.stdout + out.stderr
    if out.returncode != 0:
        tail = "\n".join(text.splitlines()[-4:])
        # exit 2 = 内容不满足；exit 3 = 检查没跑起来。两者都叫「不一致」会让维护者
        # 去改快照，而其实只是没装依赖（issue #143）。
        if out.returncode == 3:
            return False, f"could not run (environment): {tail}"
        return False, f"out of step with the authority (content): {tail}"
    m = re.search(r"keys\s*:\s*(\d+)", text)
    return True, f"aligned, {m.group(1) if m else '?'} keys"



# --- The claims ---------------------------------------------------------

# The README headline currently has two valid forms:
#   - Pre-29268b2:  "**943 loaded patterns across 67 repos.**" (with trailing `.`)
#   - Post-29268b2: "**753 loaded patterns across 67 repos, plus 190 PR observations**"
# The verifier accepts EITHER; the post-refactor form is the one we want to
# converge on, but the pre-refactor form is not "wrong", just out of date.
ALLOWED_PATTERNS_HEADLINES = [
    # Pre-refactor headline: "**943 loaded patterns across 67 repos.**"
    re.compile(
        r"\*\*(?P<patterns>\d+)\s+loaded\s+patterns\s+across\s+(?P<repos>\d+)\s+repos\.\*\*"
    ),
    # Post-29268b2 headline: "**753 loaded patterns across 67 repos**, plus 190 PR observations"
    re.compile(
        r"\*\*(?P<patterns>\d+)\s+loaded\s+patterns\s+across\s+(?P<repos>\d+)\s+repos\*\*,"
        r"\s*plus\s*(?P<observations>\d+)\s+PR\s+observations"
    ),
    # Post-readme-rewrite receipts sentence. The counts stopped being a
    # headline and became evidence for a sentence about what the corpus is.
    # The numbers are still checkable, which is the point of this gate — the
    # phrasing changed, the accountability did not.
    re.compile(
        r"(?P<patterns>\d+)\s+loaded\s+patterns,"
        r"\s*(?P<observations>\d+)\s+harvested\s+failed-PR\s+observations,"
        r"\s*(?P<repos>\d+)\s+repo\s+profiles,"
        r"\s*(?P<cases>\d+)\s+reviewed\s+cases"
    ),
]

EXPECTED_MCP_TOOLS = {
    "analyze_pr", "coach_pr", "triage_pr", "get_repo_profile",
    "list_open_prs", "get_case_study", "search_patterns", "schema_info",
    "status_prs", "profile_writeback_suggestions", "maintainer_view",
    "contributor_view", "review_queue", "prgenius_doctor",
}

def _live_repo_profiles() -> int:
    """Count profiles/ subdirectories — the live number, not a constant.

    A hardcoded expectation is the wrong shape for this check: add a profile
    and the README silently goes stale while the gate still passes. The
    README must track the tree, so compare against the tree.
    """
    d = REPO_ROOT / "profiles"
    return sum(1 for p in d.iterdir() if p.is_dir()) if d.is_dir() else 0


# --- Verifier -----------------------------------------------------------

def main() -> int:
    readme = _read("README.md")
    errors: list[str] = []

    # 1. README corpus counts (headline or receipts sentence)
    matched = False
    for pat in ALLOWED_PATTERNS_HEADLINES:
        m = pat.search(readme)
        if not m:
            continue
        matched = True
        claimed = m.groupdict()

        # Patterns = anti (md+json) + success (md+json), the same total under
        # every phrasing we have ever used.
        live_patterns = _live_anti_patterns()[0] + _live_success_patterns()
        if claimed.get("patterns") and int(claimed["patterns"]) != live_patterns:
            errors.append(
                f"README claims {claimed['patterns']} patterns, but live "
                f"({_live_anti_patterns()[0]} anti + "
                f"{_live_success_patterns()} success) = {live_patterns}"
            )
        live_repos = _live_repo_profiles()
        if claimed.get("repos") and int(claimed["repos"]) != live_repos:
            errors.append(
                f"README claims {claimed['repos']} repo profiles, but "
                f"profiles/ holds {live_repos}"
            )
        # Only the receipts phrasing claims these two; check them when present
        # rather than silently accepting a number nobody verified.
        if claimed.get("observations"):
            live_obs = _live_count("pr-observations", "*.json")
            if int(claimed["observations"]) != live_obs:
                errors.append(
                    f"README claims {claimed['observations']} PR observations, "
                    f"but pr-observations/ holds {live_obs}"
                )
        if claimed.get("cases"):
            live_cases = _live_count("review-cases", "*.json")
            if int(claimed["cases"]) != live_cases:
                errors.append(
                    f"README claims {claimed['cases']} reviewed cases, but "
                    f"review-cases/ holds {live_cases}"
                )
        break
    if not matched:
        errors.append(
            "README corpus counts do not match any known phrasing — see "
            "ALLOWED_PATTERNS_HEADLINES in scripts/verify_claims.py"
        )

    # 2. MCP tool count
    live_tools = _live_mcp_tools()
    if len(live_tools) != 14:
        errors.append(
            f"prgenius/src/prgenius/mcp.py has {len(live_tools)} @mcp.tool "
            f"decorators, expected 14"
        )

    # 3. Version alignment
    init_v = _live_init_version()
    pyproject_v = _live_pyproject_version()
    if init_v != pyproject_v:
        errors.append(
            f"version drift: prgenius/__init__.py={init_v!r} vs "
            f"prgenius/pyproject.toml={pyproject_v!r}"
        )

    # 4. CHANGELOG top entry
    cl = _read("CHANGELOG.md")
    cl_match = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", cl, re.MULTILINE)
    if cl_match:
        cl_v = cl_match.group(1)
        if cl_v != init_v:
            errors.append(
                f"CHANGELOG top entry is {cl_v}, but __init__.py is {init_v}"
            )

    # 5. DSH contract-gate count claimed in prose must equal the live gate (#136).
    #    The number moves whenever checks are added or retired, so a literal in a
    #    doc has no writer. Measure, then refuse to release while they disagree.
    live_gate = _live_contract_gate_count()
    claims = _doc_contract_claims()
    if live_gate < 0 and claims:
        errors.append(
            "scripts/check_dsh_plugin_contract.py did not report a blocking-check "
            f"count, but the docs claim one at: {[c[0] for c in claims]}"
        )
    for where, claimed in claims:
        if live_gate >= 0 and claimed != live_gate:
            errors.append(
                f"{where} claims {claimed} blocking checks, but "
                f"check_dsh_plugin_contract.py reports {live_gate}. "
                f"Update the doc — or stop stating a number that has no writer."
            )

    # 6. Slot-catalog snapshot must match its authority (#139). It was red on main
    #    for weeks while releases kept tagging — the 宁缺勿假 gate silently declines
    #    seats the host actually offers once the table falls behind.
    aligned, detail = _slot_catalog_alignment()
    if not aligned:
        errors.append(f"slot catalog snapshot is not aligned: {detail}")

    # --- Report ---
    if errors:
        print("❌ verify_claims.py — drift detected:")
        for e in errors:
            print(f"  - {e}")
        print()
        print("Fix the source of drift BEFORE tagging a release. The three")
        print("retracted releases in CHANGELOG (v2.1.0, v2.1.4, v2.2.x) all")
        print("would have been caught by a version of this gate.")
        return 1
    print("✅ verify_claims.py — all claims hold against the live tree")
    print(f"  - README pattern headline:  OK")
    print(f"  - MCP tools registered:     {len(live_tools)} (expected 14)")
    print(f"  - version init:             {init_v}")
    print(f"  - version pyproject:        {pyproject_v}")
    if cl_match:
        print(f"  - CHANGELOG top:            [{cl_match.group(1)}]")
    print(f"  - contract gate claims:     {len(claims)} doc mention(s), live={live_gate}")
    print(f"  - slot catalog:             {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
