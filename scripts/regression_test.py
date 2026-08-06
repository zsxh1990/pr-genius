#!/usr/bin/env python3
"""Regression test: verify summary field exists for all profiles."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "prgenius" / "src"))

from prgenius.evaluator import analyze_pr
from prgenius.parser import iter_profiles

def test_summary_field():
    """Verify summary field exists in coach output for all profiles."""
    repo_root = Path(__file__).parent.parent
    profiles = list(iter_profiles(repo_root))
    
    print(f"Testing {len(profiles)} profiles for summary field...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    errors = []
    
    for profile in profiles:
        folder = profile.get("folder", "")
        fm = profile.get("frontmatter", {})
        repo = fm.get("repo", folder.replace("-", "/", 1))
        gl = fm.get("agent_guidelines", {})
        
        try:
            result = analyze_pr(
                title="fix: update documentation",
                description="Update docs",
                repo=repo,
                repo_root=repo_root,
                body="This PR updates the documentation.",
                star_count=fm.get("star", 0),
                repo_merge_rate=gl.get("external_merge_rate_30", 0.0),
            )
            
            summary = result.get("summary")
            tier = result.get("tier")
            
            if summary and summary.startswith(("🟢", "🟡", "🔴")):
                passed += 1
            else:
                failed += 1
                errors.append(f"{repo}: summary='{summary}'")
                
        except Exception as e:
            failed += 1
            errors.append(f"{repo}: {e}")
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if errors:
        print("\nErrors:")
        for err in errors[:5]:
            print(f"  - {err}")
    
    print("=" * 60)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(test_summary_field())
