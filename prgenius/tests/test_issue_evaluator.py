"""Tests for issue evaluator."""
import pytest
from prgenius.issue_evaluator import analyze_issue, analyze_issues_batch


class TestAnalyzeIssue:
    def test_spam_detection(self):
        issue = {
            "title": "Buy now! Free money!",
            "body": "Click here to claim your prize",
            "labels": [],
        }
        result = analyze_issue(issue)
        assert result["is_spam"] is True
        assert result["risk"] == "critical"
        assert result["quality_grade"] == "F"

    def test_secret_detection(self):
        issue = {
            "title": "Bug report",
            "body": "Here is my token: ghp_1234567890abcdef1234567890abcdef12345678",
            "labels": [{"name": "bug"}],
        }
        result = analyze_issue(issue)
        assert result["risk"] == "high"
        assert any("secret" in i["message"].lower() for i in result["issues"])

    def test_high_quality_issue(self):
        issue = {
            "title": "Fix authentication timeout on large datasets",
            "body": "## Problem\nWhen processing >10k records, auth times out.\n\n## Expected\nShould complete within 30s.\n\n## Reproduction\n1. Load 10k records\n2. Run auth\n3. See timeout",
            "labels": [
                {"name": "bug"},
                {"name": "agent-friendly"},
                {"name": "no-credentials"},
                {"name": "has-test"},
            ],
        }
        result = analyze_issue(issue)
        assert result["score"] >= 60
        assert result["quality_grade"] in ("A", "B", "C")
        assert result["is_crawler_friendly"] is True

    def test_low_quality_issue(self):
        issue = {
            "title": "fix",
            "body": "broken",
            "labels": [],
        }
        result = analyze_issue(issue)
        assert result["score"] < 40
        assert result["quality_grade"] in ("D", "F")
        assert result["is_crawler_friendly"] is False

    def test_intake_labels(self):
        issue = {
            "title": "Missing lesson for RAG build",
            "body": "## Problem\nRAG build fails on large datasets\n\n## What was tried\nNothing yet",
            "labels": [
                {"name": "intake"},
                {"name": "pending-review"},
                {"name": "agent-friendly"},
            ],
        }
        result = analyze_issue(issue)
        assert result["score"] >= 50
        assert not any(i["severity"] == "critical" for i in result["issues"])


class TestAnalyzeIssuesBatch:
    def test_batch_analysis(self):
        issues = [
            {
                "title": "Good issue",
                "body": "## Problem\nDetailed description with reproduction steps",
                "labels": [{"name": "bug"}, {"name": "agent-friendly"}],
            },
            {
                "title": "Bad issue",
                "body": "broken",
                "labels": [],
            },
        ]
        result = analyze_issues_batch(issues)
        assert result["total"] == 2
        assert result["average_score"] > 0
        assert len(result["results"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
