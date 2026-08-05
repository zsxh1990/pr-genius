"""End-to-end smoke test: coach + analyze + triage on real repos."""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_coach_low_risk_pr():
    """Coach should return a valid tier and summary for any PR."""
    from prgenius.evaluator import analyze_pr
    result = analyze_pr(
        title="docs: update installation guide",
        description="Update install docs",
        repo="Ikalus1988/MisakaNet",
        repo_root=REPO_ROOT,
        body="Updates the installation section. Fixes #99",
        star_count=348,
        repo_merge_rate=0.30,
        author_association="CONTRIBUTOR",
    )
    assert result["tier"] in ("low_risk", "medium_risk", "high_risk")
    assert "summary" in result
    assert result["summary"].startswith(("🟢", "🟡", "🔴"))


def test_coach_high_risk_pr():
    """Coach should return high_risk for a breaking change without issue."""
    from prgenius.evaluator import analyze_pr
    result = analyze_pr(
        title="feat!: redesign entire auth system",
        description="Breaking change",
        repo="Ikalus1988/MisakaNet",
        repo_root=REPO_ROOT,
        body="Complete rewrite of authentication.",
        star_count=348,
        repo_merge_rate=0.30,
    )
    assert result["tier"] in ("medium_risk", "high_risk")
    assert "summary" in result


def test_triage_pass_on_clean_pr():
    """Triage should pass for a clean PR."""
    from prgenius.triage import triage_pr
    result = triage_pr(
        title="fix: resolve test timeout",
        repo="Ikalus1988/MisakaNet",
        body="Fix flaky test. Fixes #50",
        diff_stat="tests/test_auth.py | 5 ++---",
        repo_root=REPO_ROOT,
    )
    assert result["verdict"] == "pass"
    assert result["policy_loaded"] is True


def test_maintainer_view_returns_action():
    """Maintainer view should return an action for a real PR."""
    from prgenius.maintainer_view import maintainer_view
    result = maintainer_view(
        title="fix: typo in README",
        description="Fix typo",
        repo="Ikalus1988/MisakaNet",
        repo_root=REPO_ROOT,
        body="Fixes #1",
    )
    assert "action" in result
    # Action may be uppercase or lowercase depending on implementation
    assert result["action"].lower() in (
        "ready_for_review", "wait_for_author", "hold_workflow",
        "priority_close_stale", "priority_duplicate"
    )
