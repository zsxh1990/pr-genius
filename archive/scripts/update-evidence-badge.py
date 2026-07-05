#!/usr/bin/env python3
"""update-evidence-badge.py — emit a shields.io-compatible JSON for the
Evidence coverage badge.

Run from repo root. Writes `docs/badges/evidence.json`:

    {
      "schemaVersion": 1,
      "label": "evidence coverage",
      "message": "100% (11/11)",
      "color": "brightgreen"
    }

shields.io picks it up via:

    https://img.shields.io/badge/dynamic/json
      ?url=https://raw.githubusercontent.com/zsxh1990/pr-genius/main/docs/badges/evidence.json
      &label=evidence+coverage
      &query=$.message
      &colorB=<color>

The README badge URL embeds the same `url` to keep the badge always
in sync with the validator's evidence report.
"""
import argparse
import json
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/badges/evidence.json"),
        help="Output JSON file (default: docs/badges/evidence.json)",
    )
    args = parser.parse_args()

    # Run validator with --enforce-evidence and parse the count
    # We expect lines like:
    #   - <case_path>: --enforce-evidence: case-level `verified_at` required
    # Each warning corresponds to one missing case-level verified_at or evidence_urls.
    # A green status means 0 warnings -> 100% coverage.
    proc = subprocess.run(
        ["python3", "validate.py", "--enforce-evidence"],
        capture_output=True,
        text=True,
    )
    # If validator itself errored, just propagate
    if proc.returncode not in (0, 1):  # 0=clean, 1=warnings present
        raise SystemExit(f"validator exit {proc.returncode}: {proc.stderr}")

    # Count "case-level" warnings
    warnings = [
        ln
        for ln in proc.stdout.splitlines()
        if "case-level" in ln and "required" in ln
    ]
    n_warnings = len(warnings)

    # Count actual case studies in the repo
    case_files = list(Path(".").glob("*/pr-*.md"))
    total = len(case_files)

    covered = total - n_warnings
    pct = (covered / total * 100) if total else 0

    if n_warnings == 0:
        color = "brightgreen"
        message = f"100% ({covered}/{total})"
    elif pct >= 90:
        color = "yellow"
        message = f"{int(pct)}% ({covered}/{total})"
    else:
        color = "red"
        message = f"{int(pct)}% ({covered}/{total})"

    out = {
        "schemaVersion": 1,
        "label": "evidence coverage",
        "message": message,
        "color": color,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"Wrote {args.out}: {message} ({color})")


if __name__ == "__main__":
    main()