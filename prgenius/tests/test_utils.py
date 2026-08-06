"""Tests for utils module."""

import pytest
from pathlib import Path

from prgenius.utils import classify_pr, extract_signals


class TestClassifyPr:
    """Test PR classification."""

    def test_merged_pr(self):
        """Merged PR should be 'merged_success'."""
        pr = {"state": "closed", "mergedAt": "2024-01-01T00:00:00Z"}
        assert classify_pr(pr) == "merged_success"

    def test_closed_not_merged(self):
        """Closed but not merged should be 'closed_rejected'."""
        pr = {"state": "closed", "mergedAt": None}
        assert classify_pr(pr) == "closed_rejected"

    def test_closed_duplicate(self):
        """Closed with duplicate comment should be 'closed_duplicate'."""
        pr = {
            "state": "closed",
            "mergedAt": None,
            "comments": [{"body": "This is a duplicate of #123"}],
        }
        assert classify_pr(pr) == "closed_duplicate"

    def test_open_pr_with_reviews(self):
        """Open PR with reviews should be classified."""
        pr = {
            "state": "open",
            "reviews": [{"state": "APPROVED"}],
            "comments": [],
        }
        result = classify_pr(pr)
        assert "review" in result or "open" in result

    def test_open_pr_no_reviews(self):
        """Open PR without reviews should be 'open_pending'."""
        pr = {"state": "open", "reviews": [], "comments": []}
        assert classify_pr(pr) == "open_pending"


class TestExtractSignals:
    """Test signal extraction."""

    def test_returns_dict(self):
        """Should return a dict with signal keys."""
        pr = {"labels": [], "title": "fix: typo", "body": "Fixes #1"}
        signals = extract_signals(pr)
        assert isinstance(signals, dict)

    def test_has_issue_link(self):
        """Should detect issue link."""
        pr = {"body": "Fixes #123"}
        signals = extract_signals(pr)
        assert signals["has_issue_link"] is True

    def test_no_issue_link(self):
        """Should detect no issue link."""
        pr = {"body": "Just a fix"}
        signals = extract_signals(pr)
        assert signals["has_issue_link"] is False

    def test_is_bug_fix(self):
        """Should detect bug fix."""
        pr = {"title": "fix: typo in README"}
        signals = extract_signals(pr)
        assert signals["is_bug_fix"] is True

    def test_is_feature(self):
        """Should detect feature."""
        pr = {"title": "feat: add new feature"}
        signals = extract_signals(pr)
        assert signals["is_feature"] is True

    def test_is_docs_only(self):
        """Should detect docs-only change."""
        pr = {"title": "docs: update README"}
        signals = extract_signals(pr)
        assert signals["is_docs_only"] is True

    def test_has_breaking_change(self):
        """Should detect breaking change from title keywords."""
        pr = {"title": "feat: breaking change in auth", "body": ""}
        signals = extract_signals(pr)
        assert signals["has_breaking_change"] is True

    def test_is_bot_pr(self):
        """Should detect bot PR from title."""
        pr = {"title": "chore: dependabot bump lodash"}
        signals = extract_signals(pr)
        assert signals["is_bot_pr"] is True

    def test_is_dependency_update(self):
        """Should detect dependency update."""
        pr = {"title": "chore: bump axios to 1.0"}
        signals = extract_signals(pr)
        assert signals["is_dependency_update"] is True

    def test_empty_pr(self):
        """Should handle empty PR."""
        pr = {}
        signals = extract_signals(pr)
        assert isinstance(signals, dict)
        assert "has_issue_link" in signals

    def test_small_pr(self):
        """Should detect small PR."""
        pr = {"title": "fix: typo", "changedFiles": 1, "additions": 5, "deletions": 2}
        signals = extract_signals(pr)
        assert signals["is_small_pr"] is True
        assert signals["is_large_pr"] is False

    def test_large_pr(self):
        """Should detect large PR."""
        pr = {"title": "feat: new module", "changedFiles": 20, "additions": 500, "deletions": 100}
        signals = extract_signals(pr)
        assert signals["is_large_pr"] is True
        assert signals["is_small_pr"] is False
