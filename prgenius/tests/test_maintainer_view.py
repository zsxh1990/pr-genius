"""Tests for PR Genius maintainer view (v1.5.0).

Locks the 5-action mapping + anti-pattern filter + informational checklist filter.
"""
import unittest
from unittest.mock import patch

from prgenius.maintainer_view import (
    MaintainerAction,
    _collect_blocking_items,
    route_action,
    _build_next_step,
    maintainer_view,
    build_review_queue,
)


def _make_result(negative=None, checklist=None):
    """Build a minimal analyze_pr result dict."""
    return {
        "tier": "high_risk" if negative else "low_risk",
        "signals": {
            "positive": [],
            "negative": negative or [],
            "neutral": [],
        },
        "checklist": checklist or [],
    }


class TestRouteAction(unittest.TestCase):
    """5-class mapping: READY / WAIT / CLOSE_DUPLICATE / CLOSE_STALE / HOLD."""

    def test_ready_for_review_no_blocking(self):
        result = _make_result()
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.READY_FOR_REVIEW)
        self.assertEqual(blocking, [])

    def test_wait_for_author_dco_p0_checklist(self):
        """P0 checklist hint with DCO keyword → WAIT_FOR_AUTHOR."""
        result = _make_result(checklist=[
            {"done": False, "priority": "P0", "action": "dco_signoff", "hint": "使用 git commit -s 添加 DCO sign-off"},
        ])
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.WAIT_FOR_AUTHOR)
        self.assertIn("DCO", reason)
        self.assertIn("dco_signoff", blocking)

    def test_wait_for_author_ci_failing_negative(self):
        result = _make_result(negative=[
            {"key": "ci_passing", "description": "CI failure", "severity": "high", "fix_action": "fix CI", "source_pr": ""},
        ])
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.WAIT_FOR_AUTHOR)
        self.assertIn("CI", reason)

    def test_close_stale_or_risky_dco_shape_stale(self):
        """All three conditions present → CLOSE_STALE_OR_RISKY."""
        result = _make_result(
            negative=[
                {"key": "dco_failed", "description": "DCO check failed", "severity": "high", "fix_action": "", "source_pr": ""},
                {"key": "shape_risk", "description": "destructive rewrite", "severity": "high", "fix_action": "", "source_pr": ""},
                {"key": "stale", "description": "no response for 30 days", "severity": "medium", "fix_action": "", "source_pr": ""},
            ],
        )
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.CLOSE_STALE_OR_RISKY)

    def test_close_duplicate(self):
        result = _make_result(negative=[
            {"key": "duplicate_pr", "description": "duplicate of #100", "severity": "high", "fix_action": "", "source_pr": ""},
        ])
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.CLOSE_DUPLICATE)

    def test_hold_workflow(self):
        result = _make_result(negative=[
            {"key": "workflow_change", "description": "modifies .github/workflows/", "severity": "high", "fix_action": "", "source_pr": ""},
        ])
        action, reason, blocking = route_action(result)
        self.assertEqual(action, MaintainerAction.HOLD_MAINTAINER_DECISION)

    def test_priority_workflow_beats_duplicate(self):
        """HOLD wins over CLOSE_DUPLICATE — workflow change always needs maintainer."""
        result = _make_result(negative=[
            {"key": "workflow_change", "description": "modifies .github/workflows/", "severity": "high", "fix_action": "", "source_pr": ""},
            {"key": "duplicate_pr", "description": "duplicate of #100", "severity": "high", "fix_action": "", "source_pr": ""},
        ])
        action, _, _ = route_action(result)
        self.assertEqual(action, MaintainerAction.HOLD_MAINTAINER_DECISION)

    def test_priority_close_stale_beats_wait(self):
        """CLOSE_STALE_OR_RISKY beats WAIT_FOR_AUTHOR when all 3 conditions present."""
        result = _make_result(
            negative=[
                {"key": "dco_failed", "description": "DCO check failed", "severity": "high", "fix_action": "", "source_pr": ""},
                {"key": "ci_failing", "description": "CI failing", "severity": "high", "fix_action": "", "source_pr": ""},
                {"key": "shape_risk", "description": "destructive", "severity": "high", "fix_action": "", "source_pr": ""},
                {"key": "stale", "description": "no response for 30 days", "severity": "medium", "fix_action": "", "source_pr": ""},
            ],
        )
        action, _, _ = route_action(result)
        self.assertEqual(action, MaintainerAction.CLOSE_STALE_OR_RISKY)


class TestAntiPatternFilter(unittest.TestCase):
    """Anti-pattern hit (e.g. anthropics-anthropic-sdk-python-1757) is NOT blocking."""

    def test_anti_pattern_key_filtered_out(self):
        result = _make_result(negative=[
            {"key": "anthropics-anthropic-sdk-python-1757", "description": "some match", "severity": "medium", "fix_action": "", "source_pr": ""},
        ])
        cats = _collect_blocking_items(result)
        # Anti-pattern hit should be filtered out of negative before routing
        self.assertEqual(len(cats["dco"]), 0)
        self.assertEqual(len(cats["ci"]), 0)
        self.assertEqual(len(cats["shape"]), 0)
        self.assertEqual(len(cats["audit"]), 0)

    def test_real_ci_key_not_filtered(self):
        result = _make_result(negative=[
            {"key": "ci_failing", "description": "CI red", "severity": "high", "fix_action": "", "source_pr": ""},
        ])
        cats = _collect_blocking_items(result)
        self.assertEqual(len(cats["ci"]), 1)


class TestInformationalChecklistFilter(unittest.TestCase):
    """Informational confirmation steps (P1 'verify CI passing') are NOT blocking."""

    def test_p1_verify_ci_filtered(self):
        result = _make_result(checklist=[
            {"done": False, "priority": "P1", "action": "ci_passing", "hint": "确认 CI 全部通过"},
        ])
        cats = _collect_blocking_items(result)
        self.assertEqual(len(cats["all"]), 0)

    def test_p0_dco_signoff_kept(self):
        """P0 DCO sign-off (not informational) IS blocking."""
        result = _make_result(checklist=[
            {"done": False, "priority": "P0", "action": "dco_signoff", "hint": "使用 git commit -s 添加 DCO sign-off"},
        ])
        cats = _collect_blocking_items(result)
        self.assertEqual(len(cats["dco"]), 1)

    def test_done_checklist_ignored(self):
        result = _make_result(checklist=[
            {"done": True, "priority": "P0", "action": "dco_signoff", "hint": "..."},
        ])
        cats = _collect_blocking_items(result)
        self.assertEqual(len(cats["dco"]), 0)

    def test_p2_checklist_ignored(self):
        result = _make_result(checklist=[
            {"done": False, "priority": "P2", "action": "add_issue_link", "hint": "建议在 body 中添加 Issue 关联"},
        ])
        cats = _collect_blocking_items(result)
        self.assertEqual(len(cats["all"]), 0)


class TestNextStep(unittest.TestCase):
    """Maintainer-facing next-step commands are actionable."""

    def test_dco_amend_command(self):
        blocking = ["dco_failed"]
        cmd = _build_next_step(MaintainerAction.WAIT_FOR_AUTHOR, blocking)
        self.assertIn("git commit --amend -s", cmd)
        self.assertIn("force-with-lease", cmd)

    def test_ci_fix_command(self):
        blocking = ["ci_failing"]
        cmd = _build_next_step(MaintainerAction.WAIT_FOR_AUTHOR, blocking)
        self.assertIn("CI", cmd)

    def test_ready_review_command(self):
        cmd = _build_next_step(MaintainerAction.READY_FOR_REVIEW, [])
        self.assertIn("review", cmd.lower())


class TestBuildReviewQueue(unittest.TestCase):
    """Digest generation groups PRs by action correctly."""

    def test_groups_by_action(self):
        prs = [
            {"number": 1, "repo": "org/repo", "title": "fix: a", "author": "u1", "body": ""},
            {"number": 2, "repo": "org/repo", "title": "fix: b", "author": "u2", "body": ""},
            {"number": 3, "repo": "org/repo", "title": "fix: c", "author": "u3", "body": ""},
        ]
        q = build_review_queue(prs, repo_root=".")
        self.assertEqual(q["total"], 3)
        # All empty body → READY_FOR_REVIEW
        self.assertEqual(q["summary"].get("READY_FOR_REVIEW", 0), 3)

    def test_empty_prs(self):
        q = build_review_queue([], repo_root=".")
        self.assertEqual(q["total"], 0)
        self.assertIn("Total open PRs: **0**", q["digest_markdown"])


class TestEndToEndMaintainerView(unittest.TestCase):
    """End-to-end: pass real analyze_pr call through maintainer_view."""

    @patch("prgenius.maintainer_view.analyze_pr")
    def test_returns_persona_maintainer(self, mock_analyze):
        mock_analyze.return_value = {
            "tier": "high_risk",
            "signals": {"positive": [], "negative": [], "neutral": []},
            "checklist": [
                {"done": False, "priority": "P0", "action": "dco_signoff", "hint": "使用 git commit -s"},
            ],
        }
        result = maintainer_view("fix: x", "", "org/repo")
        self.assertEqual(result["persona"], "maintainer")
        self.assertEqual(result["action"], "WAIT_FOR_AUTHOR")
        self.assertIn("dco_signoff", result["blocking_signals"])
        self.assertFalse(result["review_ready"])


if __name__ == "__main__":
    unittest.main()
