#!/usr/bin/env python3
"""Run the full enrichment and scoring pipeline.

Usage: python3 scripts/run_pipeline.py [--skip-enrich] [--skip-features] [--skip-score] [--skip-evidence]
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


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
