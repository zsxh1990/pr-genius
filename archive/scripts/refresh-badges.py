#!/usr/bin/env python3
"""refresh-badges.py — emit endpoint JSONs for dynamic shields.io badges.

Each emitted JSON follows shields.io's "endpoint" schema:
  https://shields.io/endpoint

The badge endpoints are static URLs hosted via raw.githubusercontent.com, so
they need to be regenerated on any metric change. Run this after:

- `validate.py --enforce-evidence` first warns / fails
- a new case study is added or removed
- a lesson is added or removed
- the prgenius package version is bumped

Emitted JSONs (under docs/badges/):

  - validate.json          (strict + enforce-evidence summary)
  - evidence.json          (case-level evidence coverage: 11/11)
  - round_evidence.json    (round 1 + amend rounds with verified_at)
  - profiles.json          (count of profile dirs)
  - cases.json             (count of pr-*.md case studies)
  - lessons.json           (count of misakanet-50/lesson-*.md)
  - releases.json          (count of releases, from KNOWN_ISSUES v0.7.x)
  - latest_release.json    (highest release tag visible in KNOWN_ISSUES)
  - prgenius_version.json  (from prgenius/src/prgenius/__init__.py)
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BADGES = ROOT / "docs" / "badges"
BADGES.mkdir(parents=True, exist_ok=True)


def count_files(pattern_glob):
    return len(list(ROOT.glob(pattern_glob)))


def count_case_studies():
    return len(list(ROOT.glob("*/pr-*.md")))


def count_lessons():
    return len(list((ROOT / "misakanet-50").glob("lesson-*.md")))


def count_profiles():
    """Count directories whose name is a profile (Org-Repo slug) and
    that contain index.md. Excludes root (.), docs/, archive/, scripts/,
    misakanet-50/, prgenius/, anti-patterns/, data/, .github/.
    """
    excluded = {
        "docs", "archive", "scripts", "misakanet-50", "prgenius",
        "anti-patterns", "data", ".github",
    }
    return sum(
        1 for d in ROOT.iterdir()
        if d.is_dir()
        and d.name not in excluded
        and (d / "index.md").exists()
    )


def case_evidence_coverage():
    """Return (covered, total) for case-level evidence."""
    total = count_case_studies()
    covered = 0
    for cf in ROOT.glob("*/pr-*.md"):
        text = cf.read_text(encoding="utf-8")
        fm = text.split("---")[1] if "---" in text else ""
        if "verified_at:" in fm and "evidence_urls:" in fm:
            covered += 1
    return covered, total


def round_evidence_coverage():
    """Return (covered, total) for round-level evidence on rounds that *should*
    have evidence (open / amend / merge / close / decision / bot_review /
    human_review). Excludes check_in / bump rounds: they're meta-rounds about
    maintainer response timing, not about diff content, so requiring GH API
    evidence would be the wrong gate.

    A round is considered covered when its chunk contains a `      verified_at:`
    line at the delta level.
    """
    actionable_actions = {
        "open", "amend", "merge", "close", "decision", "bot_review",
        "human_review",
    }
    total = 0
    covered = 0
    for cf in ROOT.glob("*/pr-*.md"):
        text = cf.read_text(encoding="utf-8")
        fm_match = re.search(r"^rounds:\n((?:[ \t]+- round:\s*\d+.*\n(?:[ \t]+[^\n]*\n)*)+)",
                             text, re.MULTILINE)
        if not fm_match:
            continue
        rounds_block = fm_match.group(1)
        round_starts = list(re.finditer(r"^[ \t]+- round:\s*(\d+)", rounds_block, re.MULTILINE))
        for i, m in enumerate(round_starts):
            end = round_starts[i + 1].start() if i + 1 < len(round_starts) else len(rounds_block)
            chunk = rounds_block[m.start():end]
            action_m = re.search(r"^[ \t]+action:\s*(\w+)", chunk, re.MULTILINE)
            action = action_m.group(1) if action_m else None
            if action not in actionable_actions:
                continue  # skip check_in / bump
            total += 1
            if re.search(r"^[ \t]+verified_at:", chunk, re.MULTILINE):
                covered += 1
    return covered, total


def validate_state():
    out = subprocess.run(
        ["python3", "validate.py", "--strict"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if "All checks passed" in out.stdout:
        return "passing", "brightgreen"
    return "failing", "red"


def latest_release_tag():
    """Highest released X.Y.Z from CHANGELOG (sections with Compare: lines)."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    sections = re.split(r"^##\s*\[v?(\d+\.\d+\.\d+)\]\s*-\s*\d{4}-\d{2}-\d{2}",
                        text, flags=re.MULTILINE)
    versions = set()
    for i in range(1, len(sections), 2):
        version = sections[i]
        body = sections[i + 1] if i + 1 < len(sections) else ""
        if "Compare:" in body:
            versions.add(version)
    if not versions:
        return "v0.0.0"
    return "v" + max(versions, key=lambda v: tuple(int(p) for p in v.split(".")))


def prgenius_version():
    init = (ROOT / "prgenius" / "src" / "prgenius" / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', init)
    return m.group(1) if m else "0.0.0"


def release_count():
    """Count CHANGELOG sections for v0.6.0+ that have a `Compare:` line —
    those are releases with a corresponding GitHub Release tag. Pre-v0.6
    sections are historical docs without GH releases."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    # Split on `## [vX.Y.Z]` headings, keep those with a Compare line and
    # version >= 0.6.0.
    sections = re.split(r"^##\s*\[v?(\d+\.\d+\.\d+)\]\s*-\s*\d{4}-\d{2}-\d{2}",
                        text, flags=re.MULTILINE)
    # sections[0] is preamble, then alternating [version, body, version, body, ...]
    count = 0
    for i in range(1, len(sections), 2):
        version = sections[i]
        body = sections[i + 1] if i + 1 < len(sections) else ""
        # Filter: >= 0.6.0 and has Compare: line
        major_minor = tuple(int(p) for p in version.split(".")[:2])
        if major_minor >= (0, 6) and "Compare:" in body:
            count += 1
    return count


def write_badge(name, label, message, color):
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
    }
    out = BADGES / f"{name}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {out.relative_to(ROOT)}")


def main():
    print(f"Regenerating badges in {BADGES.relative_to(ROOT)}/")

    covered, total = case_evidence_coverage()
    pct = int(round(100 * covered / total)) if total else 0
    color = "brightgreen" if pct == 100 else "yellow" if pct >= 80 else "red"
    write_badge("evidence", "evidence coverage",
                f"{pct}% ({covered}/{total})", color)

    rcov, rtotal = round_evidence_coverage()
    rpct = int(round(100 * rcov / rtotal)) if rtotal else 0
    rcolor = "brightgreen" if rpct == 100 else "yellow" if rpct >= 80 else "red"
    write_badge("round_evidence", "round evidence",
                f"{rpct}% ({rcov}/{rtotal})", rcolor)

    profiles = count_profiles()
    write_badge("profiles", "profiles", str(profiles),
                "blue" if profiles >= 10 else "lightgrey")

    cases = count_case_studies()
    write_badge("cases", "case studies", str(cases),
                "blue" if cases >= 10 else "lightgrey")

    lessons = count_lessons()
    write_badge("lessons", "lessons", str(lessons),
                "blue" if lessons >= 10 else "lightgrey")

    status, color = validate_state()
    write_badge("validate", "validate --strict",
                status, color)

    pgv = prgenius_version()
    write_badge("prgenius_version", "prgenius", pgv,
                "blue" if pgv != "0.0.0" else "lightgrey")

    latest = latest_release_tag()
    write_badge("latest_release", "latest release", latest, "blue")

    rel_count = release_count()
    write_badge("releases", "releases", str(rel_count), "blue")


if __name__ == "__main__":
    main()