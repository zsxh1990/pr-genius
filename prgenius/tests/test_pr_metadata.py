"""Tests for PR metadata extraction (Phase 5.1)."""

import pytest
from pathlib import Path

from prgenius.pr_metadata import (
    assess_impact,
    assess_review_complexity,
    parse_diff_stat,
    ImpactAssessment,
    ReviewComplexity,
)


class TestParseDiffStat:
    """Test diff stat parsing."""

    def test_full_diff_stat(self):
        """Parse '3 files changed, 10 insertions(+), 5 deletions(-)'."""
        files, added, deleted = parse_diff_stat(
            "3 files changed, 10 insertions(+), 5 deletions(-)"
        )
        assert files == 3
        assert added == 10
        assert deleted == 5

    def test_single_file_diff(self):
        """Parse single file diff stat."""
        files, added, deleted = parse_diff_stat("file.py | 10 +++--")
        assert files == 1
        assert added == 10

    def test_empty_diff_stat(self):
        """Handle empty diff stat."""
        files, added, deleted = parse_diff_stat("")
        assert files == 0
        assert added == 0
        assert deleted == 0

    def test_none_diff_stat(self):
        """Handle None diff stat."""
        files, added, deleted = parse_diff_stat(None)
        assert files == 0


class TestAssessImpact:
    """Test impact assessment."""

    def test_simple_fix(self):
        """Simple fix has low impact."""
        impact = assess_impact(
            title="fix: typo in README",
            body="Fixes #1",
        )
        assert impact.breaking_change is False
        assert impact.security_sensitive is False
        assert impact.dependency_changes is False

    def test_breaking_change_conventional_commit(self):
        """Detect breaking change from conventional commit."""
        impact = assess_impact(
            title="feat!: redesign auth system",
            body="Breaking change",
        )
        assert impact.breaking_change is True

    def test_breaking_change_body(self):
        """Detect breaking change from body."""
        impact = assess_impact(
            title="feat: new API",
            body="This is a breaking change that removes the old endpoint",
        )
        assert impact.breaking_change is True

    def test_security_sensitive_title(self):
        """Detect security-sensitive from title."""
        impact = assess_impact(
            title="fix: OAuth token refresh vulnerability",
            body="Fixes CVE-2024-1234",
        )
        assert impact.security_sensitive is True

    def test_security_sensitive_body(self):
        """Detect security-sensitive from body."""
        impact = assess_impact(
            title="fix: auth issue",
            body="This fixes a XSS vulnerability in the login form",
        )
        assert impact.security_sensitive is True

    def test_dependency_changes(self):
        """Detect dependency changes."""
        impact = assess_impact(
            title="chore: update dependencies",
            body="Update deps",
            diff_stat="requirements.txt | 5 ++---\npackage.json | 3 ++-",
        )
        assert impact.dependency_changes is True

    def test_scope_detection(self):
        """Detect scope from title/body."""
        impact = assess_impact(
            title="test: add auth tests",
            body="Add tests for the auth module",
        )
        assert "tests" in impact.scope

    def test_lines_from_diff_stat(self):
        """Extract lines from diff stat."""
        impact = assess_impact(
            title="feat: new feature",
            body="Add feature",
            diff_stat="5 files changed, 100 insertions(+), 20 deletions(-)",
        )
        assert impact.files_changed == 5
        assert impact.lines_added == 100
        assert impact.lines_deleted == 20


class TestAssessReviewComplexity:
    """Test review complexity assessment."""

    def test_low_complexity(self):
        """Small PR has low complexity."""
        impact = ImpactAssessment(files_changed=1, lines_added=10)
        review = assess_review_complexity(impact)
        assert review.level == "low"
        assert review.estimated_minutes == 5

    def test_medium_complexity(self):
        """Medium PR has medium complexity."""
        impact = ImpactAssessment(files_changed=5, lines_added=100)
        review = assess_review_complexity(impact)
        assert review.level == "medium"
        assert review.estimated_minutes == 15

    def test_high_complexity(self):
        """Large PR has high complexity."""
        impact = ImpactAssessment(files_changed=20, lines_added=500)
        review = assess_review_complexity(impact)
        assert review.level == "high"
        assert review.estimated_minutes == 30

    def test_breaking_change_increases_complexity(self):
        """Breaking change increases complexity."""
        impact = ImpactAssessment(files_changed=1, lines_added=10, breaking_change=True)
        review = assess_review_complexity(impact)
        assert review.level == "high"
        assert review.estimated_minutes == 30

    def test_security_increases_complexity(self):
        """Security-sensitive increases complexity."""
        impact = ImpactAssessment(files_changed=1, lines_added=10, security_sensitive=True)
        review = assess_review_complexity(impact)
        assert review.level == "high"
        assert review.estimated_minutes == 30

    def test_domain_expert_needed(self):
        """Algorithm/architecture work needs domain expert."""
        impact = ImpactAssessment(files_changed=5, lines_added=100)
        review = assess_review_complexity(
            impact,
            title="refactor: optimize search algorithm",
            body="New optimization with benchmark results",
        )
        assert review.needs_domain_expert is True
