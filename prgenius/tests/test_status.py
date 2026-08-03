"""Tests for PR Genius status classifier.

Locks down priority rules to prevent regressions.
"""
import unittest
from datetime import datetime, timezone, timedelta

from prgenius.status import (
    PRStatus, PRInfo, classify_pr, _resolve_stale_days, _compute_transitions,
    enrich_pr_flags, format_transitions, format_step_summary,
    format_step_summary_analyze, format_issue_body, notify_webhook,
    DEFAULT_ABANDON_DAYS,
)


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


class TestSnapshotDiscovery(unittest.TestCase):
    """Snapshot file discovery must be strict to avoid picking test fixtures."""

    def _write(self, d, name, content):
        from pathlib import Path
        p = Path(d) / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_strict_date_match_skips_fixtures(self, tmp_path=None):
        import tempfile
        from pathlib import Path
        from prgenius.status import _find_latest_snapshot, _SNAPSHOT_NAME
        with tempfile.TemporaryDirectory() as td:
            # Real snapshot for today
            self._write(td, "2026-08-02.json", '{"prs": []}')
            # Test fixture that shares the date prefix — must NOT be selected
            self._write(td, "2026-08-02-graphql.json", '{"fixture": true}')
            # Older real snapshot
            self._write(td, "2026-08-01.json", '{"prs": []}')
            # Non-date filename — must NOT be selected
            self._write(td, "README.json", '{"readme": true}')

            latest = _find_latest_snapshot(Path(td))
            self.assertIsNotNone(latest)
            self.assertEqual(latest.name, "2026-08-02.json")

    def test_empty_dir_returns_none(self):
        import tempfile
        from pathlib import Path
        from prgenius.status import _find_latest_snapshot
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(_find_latest_snapshot(Path(td)))

    def test_snapshot_name_regex_shape(self):
        from prgenius.status import _SNAPSHOT_NAME
        # Strict YYYY-MM-DD.json only
        self.assertIsNotNone(_SNAPSHOT_NAME.match("2026-08-02.json"))
        self.assertIsNone(_SNAPSHOT_NAME.match("2026-08-02-graphql.json"))
        self.assertIsNone(_SNAPSHOT_NAME.match("2026-8-2.json"))  # zero-pad required
        self.assertIsNone(_SNAPSHOT_NAME.match("2026-08-02.JSON"))  # case-sensitive
        self.assertIsNone(_SNAPSHOT_NAME.match("README.json"))


class TestSnapshotSaveTimestamp(unittest.TestCase):
    """Snapshot save should include HHMM so multiple runs per day are kept."""

    def test_save_snapshot_filename_has_hhmm(self):
        import tempfile
        from pathlib import Path
        from prgenius.status import _save_snapshot
        with tempfile.TemporaryDirectory() as td:
            p = _save_snapshot({"prs": []}, Path(td))
            # Pattern: YYYY-MM-DD-HHMM.json
            self.assertRegex(p.name, r"^\d{4}-\d{2}-\d{2}-\d{4}\.json$")

    def test_save_snapshot_distinct_files_across_runs(self):
        """Two save calls produce different filenames (HHMM keeps collisions
        to within 1 minute, which cron never hits)."""
        import tempfile
        from pathlib import Path
        from prgenius.status import _save_snapshot
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            p1 = _save_snapshot({"prs": [], "n": 1}, d)
            # Force a different minute by renaming the first file
            stem = p1.name[:-5]  # strip .json
            new_first = d / (stem[:-4] + "0000.json")  # rewrite HHMM to 0000
            p1.rename(new_first)
            p2 = _save_snapshot({"prs": [], "n": 2}, d)
            self.assertNotEqual(new_first.name, p2.name)


class TestStaleDaysSourceReporting(unittest.TestCase):
    """check_status must report the actual stale_days_source per run."""

    def _run_with_empty_fetch(self, **kwargs):
        from prgenius import status as st_mod
        original = st_mod.fetch_open_prs
        st_mod.fetch_open_prs = lambda **kw: []
        try:
            from prgenius.status import check_status
            return check_status(save_snapshot=False, **kwargs)
        finally:
            st_mod.fetch_open_prs = original

    def test_cli_source(self):
        r = self._run_with_empty_fetch(author="zsxh1990", stale_days=7, repo_root=None)
        self.assertEqual(r["stale_days_source"], "cli")
        self.assertEqual(r["stale_days"], 7)

    def test_default_source_when_no_profile(self):
        r = self._run_with_empty_fetch(author="zsxh1990", repo_root=None)
        self.assertEqual(r["stale_days_source"], "default")
        self.assertEqual(r["stale_days"], 14)


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

    def test_severity_critical(self):
        """WAITING → NEEDS_REBASE has severity=critical."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "NEEDS_REBASE"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertTrue(transitions[0]["alert"])
        self.assertEqual(transitions[0]["severity"], "critical")

    def test_severity_info(self):
        """STALE_REVIEW → CLEAN has severity=info."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "CLEAN"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "STALE_REVIEW"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertTrue(transitions[0]["alert"])
        self.assertEqual(transitions[0]["severity"], "info")

    def test_no_severity_for_non_alert(self):
        """WAITING → BLOCKED has no severity (not an alert)."""
        current = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "BLOCKED"},
        ])
        previous = self._make_result([
            {"repo": "org/repo", "number": 1, "title": "PR1", "status": "WAITING"},
        ])
        transitions = _compute_transitions(current, previous)
        self.assertFalse(transitions[0]["alert"])
        self.assertNotIn("severity", transitions[0])


class TestProfileWriteback(unittest.TestCase):
    """Profile writeback suggestions."""

    def test_stale_no_review_suggests_threshold(self):
        """STALE_NO_REVIEW with >21d suggests stale_days_threshold."""
        from prgenius.status import suggest_profile_writeback
        result = {
            "prs": [{
                "repo": "org/repo",
                "number": 1,
                "title": "old PR",
                "status": "STALE_NO_REVIEW",
                "days_since_update": 30,
            }],
        }
        suggestions = suggest_profile_writeback(result, mode="suggest")
        self.assertTrue(any(s["field"] == "stale_days_threshold" for s in suggestions))

    def test_auto_mode_filters_low_confidence(self):
        """auto mode only returns suggestions with confidence >= 0.8."""
        from prgenius.status import suggest_profile_writeback
        result = {
            "prs": [{
                "repo": "org/repo",
                "number": 1,
                "title": "old PR",
                "status": "STALE_NO_REVIEW",
                "days_since_update": 30,
            }],
        }
        suggestions = suggest_profile_writeback(result, mode="auto")
        for s in suggestions:
            self.assertGreaterEqual(s["confidence"], 0.8)

    def test_no_suggestions_for_healthy_prs(self):
        """No writeback suggestions for WAITING/BLOCKED PRs."""
        from prgenius.status import suggest_profile_writeback
        result = {
            "prs": [{
                "repo": "org/repo",
                "number": 1,
                "title": "healthy PR",
                "status": "WAITING",
                "days_since_update": 3,
            }],
        }
        suggestions = suggest_profile_writeback(result, mode="suggest")
        self.assertEqual(len(suggestions), 0)


class TestEnrichPrFlags(unittest.TestCase):
    """Phase 4: enrich_pr_flags adds abandon/ping/rebase flags."""

    def test_stale_no_review_becomes_ping(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            last_review_at="",
            updated_at=(now - timedelta(days=20)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        result = enrich_pr_flags(result)
        self.assertTrue(result.ping_suggested)
        self.assertFalse(result.abandon_candidate)
        self.assertFalse(result.rebase_suggested)

    def test_stale_no_review_becomes_abandon(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            last_review_at="",
            updated_at=(now - timedelta(days=60)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        result = enrich_pr_flags(result)
        self.assertTrue(result.abandon_candidate)
        self.assertFalse(result.ping_suggested)  # abandon overrides ping

    def test_stale_review_becomes_ping(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            last_commit_at=(now - timedelta(days=20)).isoformat(),
            last_review_at=(now - timedelta(days=25)).isoformat(),
            updated_at=(now - timedelta(days=1)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        result = enrich_pr_flags(result)
        self.assertTrue(result.ping_suggested)
        self.assertFalse(result.abandon_candidate)

    def test_needs_rebase_becomes_rebase(self):
        pr = _make_pr(mergeable="CONFLICTING")
        result = classify_pr(pr)
        result = enrich_pr_flags(result)
        self.assertTrue(result.rebase_suggested)
        self.assertFalse(result.ping_suggested)
        self.assertFalse(result.abandon_candidate)

    def test_ci_failing_becomes_abandon_after_threshold(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            checks_status="failure",
            updated_at=(now - timedelta(days=60)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        result = enrich_pr_flags(result)
        self.assertTrue(result.abandon_candidate)

    def test_changes_requested_becomes_abandon_after_threshold(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            review_decision="CHANGES_REQUESTED",
            # last_commit < last_review → classify_pr picks CHANGES_REQUESTED (not STALE_REVIEW)
            last_commit_at=(now - timedelta(days=70)).isoformat(),
            last_review_at=(now - timedelta(days=60)).isoformat(),
            updated_at=(now - timedelta(days=60)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        self.assertEqual(result.status, PRStatus.CHANGES_REQUESTED)
        result = enrich_pr_flags(result)
        self.assertTrue(result.abandon_candidate)

    def test_waiting_no_flags(self):
        pr = _make_pr()
        result = classify_pr(pr)
        result = enrich_pr_flags(result)
        self.assertFalse(result.abandon_candidate)
        self.assertFalse(result.ping_suggested)
        self.assertFalse(result.rebase_suggested)

    def test_clean_no_flags(self):
        pr = _make_pr(
            mergeable="MERGEABLE", merge_state="CLEAN", review_decision="APPROVED",
        )
        result = classify_pr(pr)
        result = enrich_pr_flags(result)
        self.assertFalse(result.abandon_candidate)
        self.assertFalse(result.ping_suggested)
        self.assertFalse(result.rebase_suggested)

    def test_custom_abandon_days(self):
        now = datetime.now(timezone.utc)
        pr = _make_pr(
            last_review_at="",
            updated_at=(now - timedelta(days=30)).isoformat(),
        )
        result = classify_pr(pr, stale_days=14)
        # With default threshold (56d), 30d is not abandon
        result_no_abandon = enrich_pr_flags(result)
        self.assertFalse(result_no_abandon.abandon_candidate)
        self.assertTrue(result_no_abandon.ping_suggested)

        # With custom threshold (21d), 30d is abandon
        result_abandon = enrich_pr_flags(result, abandon_days=21)
        self.assertTrue(result_abandon.abandon_candidate)


class TestFormatTransitions(unittest.TestCase):
    """Phase 2: format_transitions with recommended actions."""

    def test_critical_alert_has_action(self):
        transitions = [{
            "repo": "org/repo", "number": 1, "title": "PR",
            "previous_status": "WAITING", "current_status": "CI_FAILING",
            "changed": True, "alert": True, "severity": "critical",
        }]
        text = format_transitions(transitions)
        self.assertIn("🚨", text)
        self.assertIn("investigate CI failure", text)

    def test_info_alert_has_action(self):
        transitions = [{
            "repo": "org/repo", "number": 1, "title": "PR",
            "previous_status": "STALE_REVIEW", "current_status": "CLEAN",
            "changed": True, "alert": True, "severity": "info",
        }]
        text = format_transitions(transitions)
        self.assertIn("ℹ️", text)
        self.assertIn("ready for merge", text)

    def test_non_alert_no_action(self):
        transitions = [{
            "repo": "org/repo", "number": 1, "title": "PR",
            "previous_status": None, "current_status": "WAITING",
            "changed": True, "alert": False,
        }]
        text = format_transitions(transitions)
        self.assertIn("NEW", text)
        self.assertNotIn("🚨", text)

    def test_empty_transitions(self):
        text = format_transitions([])
        self.assertEqual(text, "")


class TestFormatStepSummary(unittest.TestCase):
    """Phase 3: GitHub Step Summary formatting."""

    def _make_result(self):
        return {
            "author": "testuser",
            "checked_at": "2026-08-03T12:00:00+00:00",
            "stale_days": 14,
            "stale_days_source": "default",
            "prs": [
                {"status": "CI_FAILING", "repo": "org/repo", "number": 1,
                 "title": "fix CI", "days_since_update": 3},
            ],
            "ignored": [],
            "summary": {"ci_failing": 1},
            "transitions": [],
            "actions": ["fix CI org/repo#1"],
        }

    def test_contains_header(self):
        text = format_step_summary(self._make_result())
        self.assertIn("PR Genius Status", text)
        self.assertIn("testuser", text)

    def test_contains_pr_table(self):
        text = format_step_summary(self._make_result())
        self.assertIn("org/repo#1", text)
        self.assertIn("CI_FAILING", text)

    def test_contains_actions(self):
        text = format_step_summary(self._make_result())
        self.assertIn("fix CI org/repo#1", text)

    def test_transition_table_with_action(self):
        result = self._make_result()
        result["transitions"] = [{
            "repo": "org/repo", "number": 1, "title": "fix CI",
            "previous_status": "WAITING", "current_status": "CI_FAILING",
            "changed": True, "alert": True, "severity": "critical",
        }]
        text = format_step_summary(result)
        self.assertIn("Transition Alerts", text)
        self.assertIn("investigate CI failure", text)


class TestFormatStepSummaryAnalyze(unittest.TestCase):
    """Phase 3: analyze Step Summary formatting."""

    def test_high_risk_shows_issues(self):
        result = {
            "tier": "high_risk",
            "repo": "org/repo",
            "signals": {
                "negative": [{"description": "Missing tests", "severity": "high", "fix_action": "Add tests"}],
                "positive": [{"description": "Good message"}],
                "neutral": [],
            },
            "checklist": [{"hint": "Add tests", "priority": "P1", "done": False}],
        }
        text = format_step_summary_analyze(result)
        self.assertIn("High Risk", text)
        self.assertIn("Missing tests", text)
        self.assertIn("Add tests", text)
        self.assertIn("Good message", text)


class TestFormatIssueBody(unittest.TestCase):
    """Phase 3: issue body formatting."""

    def test_contains_title_and_table(self):
        result = {
            "author": "testuser",
            "checked_at": "2026-08-03T12:00:00+00:00",
            "summary": {"waiting": 1},
            "prs": [
                {"status": "WAITING", "repo": "org/repo", "number": 1,
                 "title": "feat", "days_since_update": 3},
            ],
            "ignored": [],
            "transitions": [],
            "actions": [],
        }
        text = format_issue_body(result)
        self.assertIn("PR Genius Heartbeat", text)
        self.assertIn("org/repo#1", text)
        self.assertIn("Auto-updated", text)

    def test_alerts_section_present(self):
        result = {
            "author": "testuser",
            "checked_at": "2026-08-03T12:00:00+00:00",
            "summary": {},
            "prs": [],
            "ignored": [],
            "transitions": [{
                "repo": "org/repo", "number": 1, "title": "PR",
                "previous_status": "WAITING", "current_status": "CI_FAILING",
                "changed": True, "alert": True, "severity": "critical",
            }],
            "actions": [],
        }
        text = format_issue_body(result)
        self.assertIn("Needs Attention", text)
        self.assertIn("investigate CI failure", text)


class TestNotifyWebhook(unittest.TestCase):
    """Phase 3: webhook notification (dry-run)."""

    def _make_result(self):
        return {
            "author": "testuser",
            "checked_at": "2026-08-03T12:00:00Z",
            "summary": {"ci_failing": 1},
            "transitions": [{
                "repo": "org/repo", "number": 1, "title": "PR",
                "previous_status": "WAITING", "current_status": "CI_FAILING",
                "changed": True, "alert": True, "severity": "critical",
            }],
            "prs": [],
            "ignored": [],
        }

    def test_feishu_dry_run(self):
        r = notify_webhook(self._make_result(), "https://open.feishu.cn/open-apis/bot/v2/hook/xxx", dry_run=True)
        self.assertTrue(r["ok"])
        self.assertTrue(r["dry_run"])
        self.assertIn("card", r["payload"])

    def test_slack_dry_run(self):
        r = notify_webhook(self._make_result(), "https://hooks.slack.com/services/xxx", dry_run=True)
        self.assertTrue(r["ok"])
        self.assertIn("blocks", r["payload"])

    def test_generic_dry_run(self):
        r = notify_webhook(self._make_result(), "https://example.com/webhook", dry_run=True)
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["payload"]["alerts"]), 1)

    def test_no_alerts_generic(self):
        result = {
            "author": "testuser",
            "checked_at": "2026-08-03T12:00:00Z",
            "summary": {},
            "transitions": [],
            "prs": [],
            "ignored": [],
        }
        r = notify_webhook(result, "https://example.com/hook", dry_run=True)
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["payload"]["alerts"]), 0)


if __name__ == "__main__":
    unittest.main()
