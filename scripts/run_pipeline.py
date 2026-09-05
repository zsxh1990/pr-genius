#!/usr/bin/env python3
"""Run the full enrichment and scoring pipeline.

Usage: python3 scripts/run_pipeline.py [--skip-enrich] [--skip-features] [--skip-score] [--skip-evidence]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
DATA_DIR = SCRIPTS_DIR.parent


def _validate_json_file(path: Path) -> str | None:
    """Validate a single JSON file. Returns error message or None."""
    try:
        size = path.stat().st_size
        if size == 0:
            return f"{path.name}: empty file (0 bytes)"
        with open(path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        return f"{path.name}: invalid JSON — {e}"
    except Exception as e:
        return f"{path.name}: {e}"
    return None


def _validate_json_dir(
    dir_path: Path, label: str, expect_file: str | None = None
) -> int:
    """Validate a directory of JSON files before a pipeline phase.

    Args:
        dir_path: The directory to validate.
        label: Human-readable label for error messages (e.g. "Phase 2 input").
        expect_file: If set, validate this specific file instead of glob *.json.

    Returns:
        Count of valid files.

    Raises:
        SystemExit: If validation fails.
    """
    if not dir_path.is_dir():
        print(f"\nVALIDATION ERROR [{label}]: directory not found: {dir_path}")
        sys.exit(1)

    if expect_file:
        target = dir_path / expect_file
        err = _validate_json_file(target)
        if err:
            print(f"\nVALIDATION ERROR [{label}]: {err}")
            sys.exit(1)
        return 1

    json_files = sorted(dir_path.glob("*.json"))
    if not json_files:
        print(f"\nVALIDATION ERROR [{label}]: no JSON files in {dir_path}")
        sys.exit(1)

    errors = []
    for jf in json_files:
        err = _validate_json_file(jf)
        if err:
            errors.append(err)

    if errors:
        print(f"\nVALIDATION ERROR [{label}]:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    return len(json_files)


def run_script(name: str, script: str) -> bool:
    """Run a pipeline script."""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script)],
        cwd=str(SCRIPTS_DIR.parent),
    )

    if result.returncode != 0:
        print(f"\nERROR: {name} failed with exit code {result.returncode}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Run PR-Genius pipeline")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip enrichment phase")
    parser.add_argument("--skip-features", action="store_true", help="Skip feature extraction")
    parser.add_argument("--skip-score", action="store_true", help="Skip scoring phase")
    parser.add_argument("--skip-evidence", action="store_true", help="Skip evidence generation")
    args = parser.parse_args()

    print("=== PR-Genius Pipeline ===\n")

    steps = [
        ("Phase 1: Enrichment", "enrich_cases.py", not args.skip_enrich),
        ("Phase 2: Feature Extraction", "extract_features.py", not args.skip_features),
        ("Phase 3: Scoring", "score_merge.py", not args.skip_score),
        ("Phase 4: Evidence Generation", "generate_evidence.py", not args.skip_evidence),
    ]

    for name, script, should_run in steps:
        if should_run:
            # --- input schema validation ---
            if "Enrichment" in name:
                n = _validate_json_dir(DATA_DIR / "review-cases", name)
                print(f"  [pre-flight] {n} case file(s) ready")
            elif "Feature Extraction" in name:
                n = _validate_json_dir(DATA_DIR / "evidence", name)
                print(f"  [pre-flight] {n} evidence file(s) ready")
            elif "Scoring" in name:
                _validate_json_dir(DATA_DIR / "features", name, expect_file="features.json")
                print(f"  [pre-flight] features.json ready")
            elif "Evidence Generation" in name:
                _validate_json_dir(DATA_DIR / "evidence", f"{name} (evidence/)")
                _validate_json_dir(DATA_DIR / "features", f"{name} (features/)", expect_file="features.json")
                n = _validate_json_dir(DATA_DIR / "predictions", f"{name} (predictions/)")
                print(f"  [pre-flight] evidence + features + {n} prediction(s) ready")

            if not run_script(name, script):
                print(f"\nPipeline stopped at: {name}")
                return 1
        else:
            print(f"\nSkipping: {name}")

    print(f"\n{'='*60}")
    print("Pipeline completed!")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
