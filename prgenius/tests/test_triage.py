"""Tests for PR triage — policy-aware screening."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prgenius.triage import triage_pr, _load_policy


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestLoadPolicy:
    def test_loads_misakanet_policy(self):
        policy = _load_policy("Ikalus1988/MisakaNet", REPO_ROOT)
        assert policy is not None
        assert policy["repo"] == "Ikalus1988/MisakaNet"
        assert len(policy["rules"]) == 9

    def test_returns_none_for_unknown_repo(self):
        policy = _load_policy("unknown/repo", REPO_ROOT)
        assert policy is None

    def test_rules_have_types(self):
        policy = _load_policy("Ikalus1988/MisakaNet", REPO_ROOT)
        hard = [r for r in policy["rules"] if r["type"] == "hard"]
        soft = [r for r in policy["rules"] if r["type"] == "soft"]
        assert len(hard) >= 4
        assert len(soft) >= 4

    def test_rules_have_anchors(self):
        policy = _load_policy("Ikalus1988/MisakaNet", REPO_ROOT)
        rules_with_anchors = [r for r in policy["rules"] if r["anchors"]]
        assert len(rules_with_anchors) >= 4


class TestTriagePr:
    def test_no_policy_repo(self):
        result = triage_pr("feat: test", "unknown/repo", repo_root=REPO_ROOT)
        # P0-A1 2026-07-19: 无 policy 仓改为 needs_preflight (克莱恩 验收门槛)
        assert result["verdict"] == "needs_preflight"
        assert result["policy_loaded"] is False
        assert len(result["generic_checks"]) == 6  # 6 条 preflight 检查清单

    def test_clean_pr_passes(self):
        result = triage_pr(
            "fix: typo",
            "Ikalus1988/MisakaNet",
            body="Fixes a typo",
            diff_stat="docs/faq.md | 3 ++-",
            repo_root=REPO_ROOT,
        )
        assert result["verdict"] == "pass"
        assert result["hard_violations"] == 0

    def test_readme_rewrite_rejected(self):
        result = triage_pr(
            "docs: update README",
            "Ikalus1988/MisakaNet",
            body="Fixes #285",
            diff_stat="README.md | 200 +++---",
            repo_root=REPO_ROOT,
        )
        assert result["verdict"] == "reject"
        assert result["hard_violations"] >= 1

    def test_generator_residual_rejected(self):
        result = triage_pr(
            "docs: add quickstart",
            "Ikalus1988/MisakaNet",
            body="Adds quickstart guide",
            diff_stat="README.md --- | 100 +++",
            repo_root=REPO_ROOT,
        )
        assert result["verdict"] == "reject"

    def test_json_format(self):
        result = triage_pr(
            "feat: test",
            "unknown/repo",
            repo_root=REPO_ROOT,
        )
        assert isinstance(result, dict)
        assert "verdict" in result
