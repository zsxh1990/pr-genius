#!/usr/bin/env python3
"""One-time migration: add case_id to review-cases/ files.

Standardizes the ID field name across evidence/ and review-cases/
so cross-referencing is possible.

evidence/ already has case_id (16 keys, richer schema).
review-cases/ has `id` with a different naming convention.

This script:
- Reads each review-cases/*.json
- Derives case_id from the filename stem (same convention as evidence/)
- Adds `case_id` field if missing or mismatched
- Preserves all existing fields
- Reports count and any inconsistencies

Does NOT modify evidence/ or enrich_cases.py.
"""

import json
import sys
from pathlib import Path

CASES_DIR = Path(__file__).parent.parent / "review-cases"


def derive_case_id_from_data(data: dict, filename_stem: str) -> str:
    """Derive case_id matching the evidence/ convention.

    evidence/ uses: repo.split('/')[-1].lower() + '-' + pr_number
    e.g., repo='actions/checkout', pr_number=2513 -> 'checkout-2513'
    """
    repo = data.get("repo", "")
    pr_number = data.get("pr_number", 0)
    if repo and pr_number:
        repo_short = repo.split("/")[-1].lower()
        return f"{repo_short}-{pr_number}"

    # Fallback: parse from filename stem
    # Filename: '{owner}-{repo}-{pr_number}'
    parts = filename_stem.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        # Try to extract repo short name from the first part
        first_parts = parts[0].rsplit("-", 1)
        if len(first_parts) == 2:
            return f"{first_parts[1].lower()}-{parts[1]}"
        return parts[1]

    return filename_stem


def migrate_file(filepath: Path, dry_run: bool = False) -> dict:
    """Migrate a single review-cases file.

    Returns:
        dict with keys: path, status, old_case_id, new_case_id
    """
    with open(filepath) as f:
        data = json.load(f)

    stem = filepath.stem
    expected_case_id = derive_case_id_from_data(data, stem)
    current_case_id = data.get("case_id")

    if current_case_id == expected_case_id:
        return {
            "path": filepath.name,
            "status": "already_ok",
            "old_case_id": current_case_id,
            "new_case_id": expected_case_id,
        }

    if not dry_run:
        data["case_id"] = expected_case_id
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return {
        "path": filepath.name,
        "status": "migrated" if not current_case_id else "corrected",
        "old_case_id": current_case_id,
        "new_case_id": expected_case_id,
    }


def main():
    dry_run = "--dry-run" in sys.argv

    case_files = sorted(CASES_DIR.glob("*.json"))
    print(f"Found {len(case_files)} review-cases files")
    if dry_run:
        print("(DRY RUN - no files will be modified)\n")
    else:
        print()

    migrated = 0
    corrected = 0
    already_ok = 0
    errors = []
    inconsistencies = []

    for fp in case_files:
        try:
            result = migrate_file(fp, dry_run=dry_run)
            if result["status"] == "migrated":
                migrated += 1
                inconsistencies.append(
                    f"  + {result['path']}: added case_id={result['new_case_id']}"
                )
            elif result["status"] == "corrected":
                corrected += 1
                inconsistencies.append(
                    f"  ~ {result['path']}: case_id {result['old_case_id']} -> {result['new_case_id']}"
                )
            else:
                already_ok += 1
        except Exception as e:
            errors.append(f"  ! {fp.name}: {e}")

    print("=== Migration Results ===")
    print(f"  Migrated (added case_id):   {migrated}")
    print(f"  Corrected (fixed case_id):  {corrected}")
    print(f"  Already OK:                 {already_ok}")
    print(f"  Errors:                     {len(errors)}")

    if inconsistencies:
        print(f"\n--- Changes ({len(inconsistencies)}) ---")
        for line in inconsistencies[:20]:
            print(line)
        if len(inconsistencies) > 20:
            print(f"  ... and {len(inconsistencies) - 20} more")

    if errors:
        print(f"\n--- Errors ({len(errors)}) ---")
        for line in errors:
            print(line)

    # Cross-reference check: verify case_id matches between evidence and review-cases
    evidence_dir = CASES_DIR.parent / "evidence"
    if evidence_dir.exists():
        evidence_case_ids = set()
        for ef in evidence_dir.glob("*.json"):
            try:
                with open(ef) as f:
                    ed = json.load(f)
                if "case_id" in ed:
                    evidence_case_ids.add(ed["case_id"])
            except Exception:
                pass

        review_case_ids = set()
        for rf in case_files:
            try:
                with open(rf) as f:
                    rd = json.load(f)
                if "case_id" in rd:
                    review_case_ids.add(rd["case_id"])
            except Exception:
                pass

        only_evidence = evidence_case_ids - review_case_ids
        only_review = review_case_ids - evidence_case_ids

        if only_evidence or only_review:
            print(f"\n=== Cross-Reference Check ===")
            if only_evidence:
                print(f"  {len(only_evidence)} case_ids only in evidence/:")
                for cid in sorted(only_evidence)[:10]:
                    print(f"    - {cid}")
            if only_review:
                print(f"  {len(only_review)} case_ids only in review-cases/:")
                for cid in sorted(only_review)[:10]:
                    print(f"    - {cid}")
        else:
            print(f"\n=== Cross-Reference Check === OK")
            print(f"  All {len(evidence_case_ids)} case_ids match between evidence/ and review-cases/")

    if not dry_run:
        print(f"\nMigration complete. Backup at review-cases.bak/")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
