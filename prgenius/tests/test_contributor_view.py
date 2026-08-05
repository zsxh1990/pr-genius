"""Tests for Contributor View (Phase 6)."""

import pytest
from pathlib import Path

from prgenius.contributor_view import (
    contributor_view,
    route_action,
    ContributorAction,
    _build_checklist,
    _collect_blocking_items,
)
from prgenius.pr_metadata import ImpactAssessment


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestRouteAction:
    """Test action routing logic."""

    def test_ready_to_submit_low_risk(self):
        """Low-risk PR should be READY_TO_SUBMIT."""
        analysis = {
            "tier": "low_risk",
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment()
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.READY_TO_SUBMIT

    def test_fix_before_submit_critical(self):
        """Critical blocking should be FIX_BEFORE_SUBMIT."""
        analysis = {
            "tier": "high_risk",
            "signals": {
                "positive": [],
                "negative": [{"key": "security-vuln", "severity": "critical"}],
                "neutral": [],
            },
        }
        impact = ImpactAssessment()
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.FIX_BEFORE_SUBMIT

    def test_needs_discussion_breaking_change(self):
        """Breaking change should be NEEDS_DISCUSSION."""
        analysis = {
            "tier": "high_risk",
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment(breaking_change=True)
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.NEEDS_DISCUSSION

    def test_needs_discussion_security(self):
        """Security-sensitive should be NEEDS_DISCUSSION."""
        analysis = {
            "tier": "medium_risk",
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment(security_sensitive=True)
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.NEEDS_DISCUSSION

    def test_improve_chance_medium(self):
        """Medium blocking should be IMPROVE_CHANCE."""
        analysis = {
            "tier": "medium_risk",
            "signals": {
                "positive": [],
                "negative": [{"key": "no-tests", "severity": "medium"}],
                "neutral": [],
            },
        }
        impact = ImpactAssessment()
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.IMPROVE_CHANCE

    def test_ask_maintainer_unclear(self):
        """Unclear situation should be ASK_MAINTAINER."""
        analysis = {
            "tier": "medium_risk",
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment()
        action, reason = route_action(analysis, impact)
        assert action == ContributorAction.ASK_MAINTAINER


class TestBuildChecklist:
    """Test checklist generation."""

    def test_no_issue_link(self):
        """Should suggest linking an issue."""
        analysis = {
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment()
        checklist = _build_checklist(analysis, impact)
        items = [c["item"] for c in checklist]
        assert "Link an issue" in items

    def test_breaking_change_migration(self):
        """Should suggest migration path for breaking changes."""
        analysis = {
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment(breaking_change=True)
        checklist = _build_checklist(analysis, impact)
        items = [c["item"] for c in checklist]
        assert "Provide migration path for breaking change" in items

    def test_security_review(self):
        """Should suggest security review."""
        analysis = {
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment(security_sensitive=True)
        checklist = _build_checklist(analysis, impact)
        items = [c["item"] for c in checklist]
        assert "Security review required" in items

    def test_no_tests(self):
        """Should suggest adding tests."""
        analysis = {
            "signals": {"positive": [], "negative": [], "neutral": []},
        }
        impact = ImpactAssessment(scope="docs")
        checklist = _build_checklist(analysis, impact)
        items = [c["item"] for c in checklist]
        assert "Add tests" in items


class TestContributorView:
    """Test full contributor view."""

    def test_returns_contributor_persona(self):
        """Should return contributor persona."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert result["persona"] == "contributor"

    def test_returns_valid_action(self):
        """Should return a valid action."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert result["action"] in [a.value for a in ContributorAction]

    def test_returns_impact(self):
        """Should return impact assessment."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            diff_stat="1 file changed, 5 insertions(+), 2 deletions(-)",
            repo_root=REPO_ROOT,
        )
        assert "impact" in result
        assert "files_changed" in result["impact"]
        assert "breaking_change" in result["impact"]

    def test_returns_review(self):
        """Should return review complexity."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert "review" in result
        assert "level" in result["review"]

    def test_returns_checklist(self):
        """Should return a checklist."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert "checklist" in result
        assert isinstance(result["checklist"], list)

    def test_returns_confidence(self):
        """Should return confidence level."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert result["confidence"] in ("low", "medium", "high")

    def test_returns_merge_probability(self):
        """Should return merge probability."""
        result = contributor_view(
            title="fix: typo",
            description="Fix typo",
            repo="org/repo",
            body="Fixes #1",
            repo_root=REPO_ROOT,
        )
        assert "merge_probability" in result
        assert 0.0 <= result["merge_probability"] <= 1.0
