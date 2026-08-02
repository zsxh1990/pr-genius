"""Tests for PR Genius status classifier.

Locks down priority rules to prevent regressions.
"""
import unittest
from datetime import datetime, timezone, timedelta

from prgenius.status import PRStatus, PRInfo, classify_pr, _resolve_stale_days, _compute_transitions


def _make_pr(**overrides) -> PRInfo:
    """Create a PRInfo with sensible defaults."""
    now = datetime.now(timezone.utc)
    defaults = {
        "repo": "org/repo",
        "number": 1,
        "title": "test PR",
        "url": "https://github.com/org/repo/pull/1",
        "author": "testuser",
        "created_at": (now - timedelta(days=5)).isoformat(),
        "updated_at": (now - timedelta(days=1)).isoformat(),
        "mergeable": "MERGEABLE",
        "merge_state": "CLEAN",
        "review_decision": "",
        "checks_status": "",
        "last_commit_at": (now - timedelta(days=3)).isoformat(),
        "last_review_at": "",
        "is_own_repo": False,
    }
    defaults.update(overrides)
    return PRInfo(**defaults)


class TestNeedsRebase(unittest.TestCase):
    """NEEDS_REBASE: CONFLICTING, DIRTY, BEHIND."""

    def test_conflicting(self):
        pr = _make_pr(mergeable="CONFLICTING")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.NEEDS_REBASE)

    def test_dirty(self):
        pr = _make_pr(merge_state="DIRTY")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.NEEDS_REBASE)

    def test_behind(self):
        pr = _make_pr(merge_state="BEHIND")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.NEEDS_REBASE)

    def test_mergeable_clean_not_rebase(self):
        pr = _make_pr(mergeable="MERGEABLE", merge_state="CLEAN")
        result = classify_pr(pr)
        self.assertNotEqual(result.status, PRStatus.NEEDS_REBASE)


class TestCiFailing(unittest.TestCase):
    """CI_FAILING: UNSTABLE, check failure."""

    def test_unstable(self):
        pr = _make_pr(merge_state="UNSTABLE")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.CI_FAILING)

    def test_check_failure(self):
        pr = _make_pr(checks_status="failure")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.CI_FAILING)

    def test_pending_not_ci_failing(self):
        """PENDING checks should be BLOCKED, not CI_FAILING."""
        pr = _make_pr(checks_status="pending")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.BLOCKED)
        self.assertNotEqual(result.status, PRStatus.CI_FAILING)


class TestStaleReviewVsChangesRequested(unittest.TestCase):
    """STALE_REVIEW must not swallow CHANGES_REQUESTED.

    STALE_REVIEW (priority 3): last_commit_at > last_review_at AND stale AND last_review_at != null
    CHANGES_REQUESTED (priority 4): reviewDecision=CHANGES_REQUESTED (and not STALE_REVIEW)
    """

    def test_stale_review_when_commit_after_review(self):
        """Pushed fix but no re-review → STALE_REVIEW."""
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            last_commit_at=(now - timedelta(days=20)).isoformat(),
            last_review_at=(now - timedelta(days=25)).isoformat(),
            updated_at=(now - timedelta(days=1)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.STALE_REVIEW)

    def test_changes_requested_when_no_commit_after_review(self):
        """Review requested but no fix pushed → CHANGES_REQUESTED."""
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            last_commit_at=(now - timedelta(days=25)).isoformat(),
            last_review_at=(now - timedelta(days=20)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.CHANGES_REQUESTED)

    def test_changes_requested_when_not_stale_yet(self):
        """Review requested, fix pushed, but not yet stale → CHANGES_REQUESTED."""
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            last_commit_at=(now - timedelta(days=5)).isoformat(),
            last_review_at=(now - timedelta(days=10)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.CHANGES_REQUESTED)

    def test_changes_requested_when_no_review_at_all(self):
        """CHANGES_REQUESTED but last_review_at is null → CHANGES_REQUESTED."""
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            last_review_at="",
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.CHANGES_REQUESTED)


class TestCleanNotSwallowedByWaiting(unittest.TestCase):
    """CLEAN must be detected before WAITING (residual fallback)."""

    def test_clean_detected(self):
        pr = _make_pr(
            mergeable="MERGEABLE",
            merge_state="CLEAN",
            review_decision="APPROVED",
        )
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.CLEAN)

    def test_waiting_is_residual(self):
        """When nothing matches, fall through to WAITING."""
        pr = _make_pr(
            mergeable="MERGEABLE",
            merge_state="CLEAN",
            review_decision="",
        )
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.WAITING)


class TestBlocked(unittest.TestCase):
    """BLOCKED: HAS_HOOKS, PENDING checks."""

    def test_has_hooks(self):
        pr = _make_pr(merge_state="HAS_HOOKS")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.BLOCKED)

    def test_blocked_state(self):
        pr = _make_pr(merge_state="BLOCKED")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.BLOCKED)

    def test_pending_checks(self):
        pr = _make_pr(checks_status="pending")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.BLOCKED)


class TestUnknown(unittest.TestCase):
    """UNKNOWN: mergeable=UNKNOWN."""

    def test_unknown_mergeable(self):
        pr = _make_pr(mergeable="UNKNOWN", merge_state="UNKNOWN")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.UNKNOWN)


class TestStaleNoReview(unittest.TestCase):
    """STALE_NO_REVIEW: no reviews and stale."""

    def test_no_review_stale(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            last_review_at="",
            updated_at=(now - timedelta(days=20)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.STALE_NO_REVIEW)

    def test_no_review_not_stale(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            last_review_at="",
            updated_at=(now - timedelta(days=5)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertNotEqual(result.status, PRStatus.STALE_NO_REVIEW)


class TestOwnRepo(unittest.TestCase):
    """OWN_REPO PRs are ignored."""

    def test_own_repo_ignored(self):
        pr = _make_pr(is_own_repo=True)
        result = classify_pr(pr)
        self.assertEqual(result.ignored_reason, "OWN_REPO")


class TestPriorityOrder(unittest.TestCase):
    """Verify priority ordering when multiple conditions match."""

    def test_needs_rebase_beats_ci_failing(self):
        """CONFLICTING + UNSTABLE → NEEDS_REBASE (priority 1 > 2)."""
        pr = _make_pr(mergeable="CONFLICTING", merge_state="UNSTABLE")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.NEEDS_REBASE)

    def test_ci_failing_beats_changes_requested(self):
        """UNSTABLE + CHANGES_REQUESTED → CI_FAILING (priority 2 > 4)."""
        pr = _make_pr(merge_state="UNSTABLE", review_decision="CHANGES_REQUESTED")
        result = classify_pr(pr)
        self.assertEqual(result.status, PRStatus.CI_FAILING)


class TestStaleDaysResolution(unittest.TestCase):
    """Priority: CLI > profile > default 14."""

    def test_cli_overrides_all(self):
        stale, source = _resolve_stale_days("org/repo", cli_stale_days=7)
        self.assertEqual(stale, 7)
        self.assertEqual(source, "cli")

    def test_default_when_no_profile(self):
        stale, source = _resolve_stale_days("org/repo", cli_stale_days=None, repo_root=None)
        self.assertEqual(stale, 14)
        self.assertEqual(source, "default")

    def test_default_when_profile_not_found(self):
        """When repo_root is given but no profile exists, use default."""
        from pathlib import Path
        stale, source = _resolve_stale_days(
            "nonexistent/repo", cli_stale_days=None,
            repo_root=Path(__file__).resolve().parents[2],
        )
        self.assertEqual(stale, 14)
        self.assertEqual(source, "default")


class TestTransitions(unittest.TestCase):
    """Transition tracking: compare current vs previous snapshot."""

    def _make_result(self, prs):
        """Helper to build a minimal result dict."""
        return {"prs": prs}

    def test_no_previous_snapshot(self):
        """First run: no transitions."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous=None)
        self.assertEqual(transitions, [])

    def test_unchanged_status(self):
        """Same status: changed=False."""
        pr = {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"}
        current = self._make_result([pr])
        previous = self._make_result([pr])
        transitions = _compute_transitions(current, previous)
        self.assertEqual(len(transitions), 1)
        self.assertFalse(transitions[0]["changed"])

    def test_changed_status(self):
        """Status changed: changed=True."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "NEEDS_REBASE"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertEqual(len(transitions), 1)
        self.assertTrue(transitions[0]["changed"])
        self.assertEqual(transitions[0]["previous_status"], "WAITING")
        self.assertEqual(transitions[0]["current_status"], "NEEDS_REBASE")

    def test_alert_escalation(self):
        """WAITING → NEEDS_REBASE triggers alert."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "NEEDS_REBASE"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertTrue(transitions[0]["alert"])

    def test_alert_deescalation(self):
        """STALE_REVIEW → CLEAN triggers alert."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "CLEAN"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "STALE_REVIEW"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertTrue(transitions[0]["alert"])

    def test_no_alert_for_minor_change(self):
        """WAITING → BLOCKED: no alert (not in alert set)."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "BLOCKED"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertFalse(transitions[0]["alert"])

    def test_disappeared_pr(self):
        """PR in previous but not current → CLOSED_OR_MERGED."""
        current = self._make_result([])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0]["current_status"], "CLOSED_OR_MERGED")
        self.assertTrue(transitions[0]["changed"])

    def test_new_pr(self):
        """PR in current but not previous → NEW."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        previous = self._make_result([])
        transitions = _compute_transitions(current, previous)
        self.assertEqual(len(transitions), 1)
        self.assertIsNone(transitions[0]["previous_status"])
        self.assertTrue(transitions[0]["changed"])


if __name__ == "__main__":
    unittest.main()
