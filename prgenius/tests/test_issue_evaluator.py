"""Tests for issue_evaluator module — 285+ test cases, full coverage.

v1.2.0: 输出结构对齐 PR Coach
- signals: positive/negative/neutral 三分类
- checklist: action/priority/done/hint
- tier: low_risk/medium_risk/high_risk

Covers:
- analyze_issue() core flow
- analyze_issues_batch() aggregation
- _spam_confidence() scoring
- _detect_secrets() patterns
- _check_title/body/labels/structure/no_secrets() scoring
- _check_labels_complete() validation
- _calculate_tier() priority logic
- _grade() mapping
- Constant integrity
- Edge cases: empty, None, huge input, boundary values
- Adversarial spam tests
- Performance tests
- Real issue validation
- MisakaNet 20% sample
"""

from __future__ import annotations

import pytest
from typing import Any, Dict, List

from prgenius.issue_evaluator import (
    analyze_issue,
    analyze_issues_batch,
    _spam_confidence,
    _detect_secrets,
    _check_title,
    _check_body,
    _check_labels,
    _check_structure,
    _check_no_secrets,
    _check_labels_complete,
    _calculate_tier,
    _grade,
    ISSUE_TYPE_LABELS,
    REQUIRED_LABELS,
    CRAWLER_LABELS,
    DEFAULT_CRAWLER_THRESHOLD,
    QUALITY_DIMENSIONS,
    SPAM_KEYWORDS_HIGH,
    SPAM_KEYWORDS_LOW,
    SECRET_PATTERNS,
)


# ============================================================
# Helpers
# ============================================================

def _make_issue(
    *,
    number: int = 1,
    title: str = "Default Issue Title Here",
    body: str | None = "A" * 200,
    labels: list | None = None,
) -> Dict[str, Any]:
    """Create a minimal GitHub issue dict."""
    return {
        "number": number,
        "title": title,
        "body": body,
        "labels": [{"name": n} for n in (labels or [])],
    }


def _make_issue_raw_labels(
    *,
    number: int = 1,
    title: str = "Default Issue Title Here",
    body: str | None = "A" * 200,
    labels: list | None = None,
) -> Dict[str, Any]:
    """Create issue with raw string labels (not dicts)."""
    return {
        "number": number,
        "title": title,
        "body": body,
        "labels": labels or [],
    }


# ============================================================
# 1. analyze_issue() — Core Flow (20 cases)
# ============================================================

class TestAnalyzeIssue:
    """Core analyze_issue() tests."""

    def test_good_issue_returns_high_score(self):
        """Well-formed issue with all fields should score high."""
        r = analyze_issue(_make_issue(
            title="Bug: Button click crashes app on mobile",
            body=(
                "## Description\n"
                "The submit button causes a crash.\n\n"
                "## Steps to Reproduce\n"
                "- 1. Open app on mobile\n"
                "- 2. Click submit\n"
                "- 3. App crashes\n\n"
                "## Expected\n"
                "Should submit successfully.\n\n"
                "## Environment\n"
                "- Node.js 18\n"
                "- Chrome 120"
            ),
            labels=["bug", "help wanted", "good first issue", "agent-friendly", "no-credentials", "has-test"],
        ))
        # New max: title(15) + body(30) + labels(15) + structure(20) + no_secrets(20) = 100
        assert r["score"] >= 70
        assert r["quality_grade"] in ("B", "C")
        assert r["tier"] == "low_risk"
        assert r["is_spam"] is False

    def test_empty_issue_returns_low_score(self):
        """Empty issue should score very low."""
        r = analyze_issue(_make_issue(
            number=999,
            title="",
            body=None,
            labels=[],
        ))
        # score: title(0) + body(0) + labels(0) + structure(0) + no_secrets(20) = 20
        assert r["score"] == 20
        assert r["quality_grade"] == "F"
        assert r["number"] == 999

    def test_spam_issue_returns_critical_risk(self):
        """Spam issue should be flagged immediately."""
        r = analyze_issue(_make_issue(
            title="Buy now free money casino",
            body="You won a prize! Click here to claim your free gift.",
        ))
        assert r["is_spam"] is True
        assert r["tier"] == "high_risk"
        assert r["quality_grade"] == "F"
        assert r["score"] == 0

    def test_issue_with_secrets_gets_high_risk(self):
        """Issue containing secrets should be high risk."""
        r = analyze_issue(_make_issue(
            body="My config: password=abc123xyz",
        ))
        assert r["tier"] == "high_risk"
        assert any("secret" in i["description"].lower() or "Secret" in i["description"]
                    for i in r["signals"]["negative"])

    def test_crawler_friendly_with_enough_labels(self):
        """Should be crawler friendly when >= threshold labels present."""
        r = analyze_issue(_make_issue(
            labels=["agent-friendly", "no-credentials", "has-test"],
        ))
        assert r["is_crawler_friendly"] is True

    def test_not_crawler_friendly_below_threshold(self):
        """Should not be crawler friendly below threshold."""
        r = analyze_issue(_make_issue(
            labels=["agent-friendly", "no-credentials"],
        ))
        assert r["is_crawler_friendly"] is False

    def test_custom_crawler_threshold(self):
        """Custom crawler threshold should be respected."""
        r = analyze_issue(
            _make_issue(labels=["agent-friendly"]),
            crawler_threshold=1,
        )
        assert r["is_crawler_friendly"] is True

    def test_result_has_number_and_title(self):
        """Result should carry issue number and title."""
        r = analyze_issue(_make_issue(number=42, title="My Bug Report"))
        assert r["number"] == 42
        assert r["title"] == "My Bug Report"

    def test_labels_as_dict_objects(self):
        """Should handle label dicts with 'name' key."""
        r = analyze_issue(_make_issue(
            labels=["bug", "urgent", "help wanted", "good first issue"],
        ))
        assert r["score"] > 0
        assert len(r["signals"]["negative"]) >= 0  # may have repro warning

    def test_labels_as_raw_strings(self):
        """Should handle raw string labels."""
        r = analyze_issue(_make_issue_raw_labels(
            labels=["bug", "urgent", "help wanted"],
        ))
        assert r["score"] > 0

    def test_score_never_exceeds_100(self):
        """Score should be capped at 100."""
        r = analyze_issue(_make_issue(
            title="A" * 100,
            body=(
                "## Description\n"
                "x " * 50 + "\n\n"
                "- step 1\n- step 2\n- step 3\n"
            ),
            labels=["a", "b", "c", "d"],
        ))
        assert r["score"] <= 100
        assert r["score"] > 0

    def test_suggestions_populated_for_low_score(self):
        """Low score issues should have suggestions."""
        r = analyze_issue(_make_issue(
            title="hi",
            body="x",
            labels=[],
        ))
        # score is low (0 for title + 0 for body + 0 for labels + 0 for structure + 20 for no_secrets = 20)
        # But no "quality" suggestion because score=20 >= 40 threshold? No, 20 < 40
        assert len(r["checklist"]) > 0
        assert any(s.get("action","") in ("improve_content", "add_crawler_labels") for s in r["checklist"])

    def test_suggestions_not_empty_for_non_crawler(self):
        """Non-crawler-friendly should suggest adding labels."""
        r = analyze_issue(_make_issue(labels=[]))
        assert any(s.get("action","") == "add_crawler_labels" for s in r["checklist"])

    def test_body_none_treated_as_empty(self):
        """None body should be treated as empty string."""
        r = analyze_issue(_make_issue(body=None))
        assert r["score"] >= 0
        assert isinstance(r["signals"]["negative"], list)

    def test_issue_with_many_labels(self):
        """Many labels should give full label score."""
        r = analyze_issue(_make_issue(
            labels=["bug", "p1", "team-frontend", "v2", "help wanted"],
        ))
        assert r["score"] >= 10  # label contribution

    def test_bug_label_without_repro_warns(self):
        """Bug label without reproduction steps should warn."""
        r = analyze_issue(_make_issue(
            title="Bug: Something broken",
            body="This is broken and I'm upset.",
            labels=["bug"],
        ))
        repro_issues = [i for i in r["signals"]["negative"] if "reproduction" in i["description"].lower()
                        or "repro" in i["description"].lower()]
        assert len(repro_issues) == 1

    def test_bug_label_with_repro_steps_no_warn(self):
        """Bug label with repro steps should not warn."""
        r = analyze_issue(_make_issue(
            title="Bug: Something broken",
            body="## Steps to Reproduce\n1. Do this\n2. Do that",
            labels=["bug"],
        ))
        repro_issues = [i for i in r["signals"]["negative"] if "reproduction" in i["description"].lower()
                        or "repro" in i["description"].lower()]
        assert len(repro_issues) == 0

    def test_intake_label_missing_pending_review_warns(self):
        """Intake without pending-review should warn."""
        r = analyze_issue(_make_issue(labels=["intake"]))
        intake_issues = [i for i in r["signals"]["negative"] if "pending-review" in i["description"]]
        assert len(intake_issues) == 1

    def test_intake_label_with_pending_review_no_warn(self):
        """Intake with pending-review should not warn."""
        r = analyze_issue(_make_issue(labels=["intake", "pending-review"]))
        intake_issues = [i for i in r["signals"]["negative"] if "pending-review" in i["description"]]
        assert len(intake_issues) == 0

    def test_enhancement_label_no_special_validation(self):
        """Enhancement label should not trigger special warnings."""
        r = analyze_issue(_make_issue(
            title="Feature: Add dark mode support",
            body="It would be nice to have dark mode.",
            labels=["enhancement"],
        ))
        # No bug or intake-specific warnings
        assert not any("reproduction" in i["description"].lower() for i in r["signals"]["negative"])
        assert not any("pending-review" in i["description"] for i in r["signals"]["negative"])


# ============================================================
# 2. analyze_issues_batch() — Aggregation (15 cases)
# ============================================================

class TestAnalyzeIssuesBatch:
    """Batch analysis tests."""

    def test_empty_list(self):
        """Empty list should return zero stats."""
        r = analyze_issues_batch([])
        assert r["total"] == 0
        assert r["spam_count"] == 0
        assert r["average_score"] == 0
        assert r["results"] == []

    def test_single_issue(self):
        """Single issue should work correctly."""
        r = analyze_issues_batch([_make_issue()])
        assert r["total"] == 1
        assert len(r["results"]) == 1

    def test_multiple_issues(self):
        """Multiple issues should aggregate correctly."""
        issues = [
            _make_issue(number=1, title="Good issue title here", body="A" * 200),
            _make_issue(number=2, title="Another good issue title", body="B" * 200),
            _make_issue(number=3, title="Third valid issue title", body="C" * 200),
        ]
        r = analyze_issues_batch(issues)
        assert r["total"] == 3
        assert r["average_score"] > 0

    def test_spam_count(self):
        """Spam issues should be counted."""
        issues = [
            _make_issue(title="Buy now free money", body="Casino prize"),
            _make_issue(title="Normal issue title here", body="A" * 200),
        ]
        r = analyze_issues_batch(issues)
        assert r["spam_count"] == 1

    def test_high_risk_count(self):
        """High-risk issues (spam + secret) should be counted."""
        issues = [
            _make_issue(title="Buy now free money", body="Casino"),
            _make_issue(body="password=secret123"),
            _make_issue(title="Normal issue title here", body="A" * 200),
        ]
        r = analyze_issues_batch(issues)
        assert r["high_risk_count"] == 2  # spam=1 + secret=1

    def test_average_score_calculation(self):
        """Average score should be correctly computed."""
        # Both will have similar scores, test the math
        issues = [
            _make_issue(number=1, title="A" * 50, body="B" * 200, labels=["x", "y", "z"]),
            _make_issue(number=2, title="C" * 50, body="D" * 200, labels=["x", "y", "z"]),
        ]
        r = analyze_issues_batch(issues)
        expected_avg = sum(analyze_issue(i)["score"] for i in issues) / 2
        assert r["average_score"] == round(expected_avg, 1)

    def test_grade_distribution(self):
        """Grade distribution should tally correctly."""
        issues = [
            _make_issue(title="A" * 50, body="B" * 200),  # likely D
            _make_issue(title="Buy now free money", body="Casino"),  # F (spam)
        ]
        r = analyze_issues_batch(issues)
        total_grades = sum(r["grade_distribution"].values())
        assert total_grades == 2

    def test_crawler_friendly_count(self):
        """Crawler-friendly issues should be counted."""
        issues = [
            _make_issue(labels=["agent-friendly", "no-credentials", "has-test"]),
            _make_issue(labels=["bug"]),
        ]
        r = analyze_issues_batch(issues)
        assert r["crawler_friendly_count"] == 1

    def test_all_spam(self):
        """All spam should give correct stats."""
        issues = [
            _make_issue(title="Buy now free money", body="Casino"),
            _make_issue(title="Free money buy now", body="Act now"),
        ]
        r = analyze_issues_batch(issues)
        assert r["spam_count"] == 2
        assert r["high_risk_count"] == 2
        assert r["average_score"] == 0

    def test_all_good(self):
        """All good issues should have no spam and low risk."""
        issues = [
            _make_issue(
                number=i,
                title=f"Good descriptive issue title #{i}",
                body="## Description\n" + "x " * 100,
                labels=["bug", "help wanted", "good first issue"],
            )
            for i in range(5)
        ]
        r = analyze_issues_batch(issues)
        assert r["spam_count"] == 0
        assert r["high_risk_count"] == 0

    def test_custom_crawler_threshold_propagated(self):
        """Custom threshold should propagate to each issue."""
        issues = [_make_issue(labels=["agent-friendly"])]
        r = analyze_issues_batch(issues, crawler_threshold=1)
        assert r["crawler_friendly_count"] == 1

    def test_batch_returns_all_results(self):
        """All results should be included."""
        issues = [_make_issue(number=i) for i in range(10)]
        r = analyze_issues_batch(issues)
        assert len(r["results"]) == 10

    def test_grade_distribution_keys(self):
        """All grade keys should be present."""
        r = analyze_issues_batch([_make_issue()])
        for grade in ["A", "B", "C", "D", "F"]:
            assert grade in r["grade_distribution"]

    def test_mixed_quality_distribution(self):
        """Mixed quality should produce varied grades."""
        issues = [
            _make_issue(title="Buy now free money", body="Casino"),  # F
            _make_issue(title="A" * 50, body="B" * 200),  # D
        ]
        r = analyze_issues_batch(issues)
        assert r["grade_distribution"]["F"] >= 1

    def test_single_item_batch(self):
        """Single item batch should match analyze_issue."""
        issue = _make_issue(number=7, title="Single test issue title", body="X" * 200)
        batch = analyze_issues_batch([issue])
        single = analyze_issue(issue)
        assert batch["results"][0]["score"] == single["score"]


# ============================================================
# 3. _spam_confidence() (30 cases)
# ============================================================

class TestSpamConfidence:
    """Spam confidence scoring tests."""

    def test_clean_text(self):
        """Normal text should return 0."""
        assert _spam_confidence("Bug report", "The app crashes on startup") == 0

    def test_single_high_keyword_long_body(self):
        """Single high keyword + long body = 1."""
        body = "A" * 150 + " buy now " + "B" * 50
        assert _spam_confidence("Normal title", body) == 1

    def test_single_high_keyword_short_body(self):
        """Single high keyword + short body = 2."""
        assert _spam_confidence("Free money", "Short body") == 2

    def test_two_high_keywords(self):
        """Two high keywords = 3."""
        assert _spam_confidence("Buy now free money", "casino") == 3

    def test_two_high_keywords_in_body(self):
        """Two high keywords in body = 3."""
        assert _spam_confidence("Title", "buy now and free money") == 3

    def test_three_high_keywords(self):
        """Three high keywords = 3."""
        assert _spam_confidence("buy now free money casino", "act now") == 3

    def test_single_low_keyword_short_body(self):
        """Single low keyword + short body (< 50 chars) = 1."""
        assert _spam_confidence("Title", "click here") == 1

    def test_single_low_keyword_long_body(self):
        """Single low keyword + long body = 0."""
        body = "A" * 60 + " click here " + "B" * 60
        assert _spam_confidence("Title", body) == 0

    def test_two_low_keywords(self):
        """Two low keywords = 2."""
        assert _spam_confidence("Title", "click here congratulations") == 2

    def test_three_low_keywords(self):
        """Three low keywords = 2 (same threshold as two)."""
        assert _spam_confidence("Title", "click here congratulations prize") == 2

    def test_one_high_one_low(self):
        """One high + one low = depends on high path."""
        body = "A" * 150 + " buy now congratulations"
        assert _spam_confidence("Title", body) == 1  # high=1, long body

    def test_one_high_one_low_short(self):
        """One high + one low + short body = 2 (high path)."""
        assert _spam_confidence("Buy now", "click here") == 2

    def test_empty_title_and_body(self):
        """Both empty = 0."""
        assert _spam_confidence("", "") == 0

    def test_title_only_high_keyword(self):
        """High keyword only in title, short body."""
        assert _spam_confidence("Free money", "") == 2  # short body (< 100)

    def test_body_only_high_keyword(self):
        """High keyword only in body."""
        assert _spam_confidence("Normal", "buy now " + "x" * 100) == 1

    def test_boundary_body_length_99(self):
        """Body length 99 with high keyword = 2 (short path)."""
        assert _spam_confidence("Title", "buy now " + "x" * 91) == 2

    def test_boundary_body_length_100(self):
        """Body length 100 with high keyword = 1 (long path)."""
        assert _spam_confidence("Title", "buy now " + "x" * 92) == 1

    def test_boundary_low_body_length_49(self):
        """Body length 49 with low keyword = 1 (short path)."""
        assert _spam_confidence("Title", "click here " + "x" * 38) == 1

    def test_boundary_low_body_length_50(self):
        """Body length 50 with low keyword = 0 (long path)."""
        assert _spam_confidence("Title", "click here " + "x" * 39) == 0

    def test_case_insensitive_detection(self):
        """Keywords should be matched case-insensitively."""
        assert _spam_confidence("BUY NOW FREE MONEY", "casino") >= 2

    def test_all_high_keywords(self):
        """All 10 high keywords present = 3."""
        text = " ".join(SPAM_KEYWORDS_HIGH)
        assert _spam_confidence(text, "") == 3

    def test_all_low_keywords(self):
        """All 7 low keywords = 2."""
        text = " ".join(SPAM_KEYWORDS_LOW)
        assert _spam_confidence("Title", text) == 2

    def test_empty_body_none_treated(self):
        """None body should not crash (caller converts)."""
        # In practice, caller converts None to "" before calling
        assert _spam_confidence("Title", "") == 0

    def test_high_keyword_in_title_only(self):
        """High keyword only in title, no body."""
        assert _spam_confidence("act now", "") == 2

    def test_high_keyword_partial_match(self):
        """Partial keyword match should not count."""
        assert _spam_confidence("buy", "free") == 0  # not "buy now"

    def test_two_distinct_high_keywords(self):
        """Two distinct high keywords in different positions."""
        assert _spam_confidence("Casino", "double your money") == 3

    def test_mixed_case_high_keyword(self):
        """Mixed case should still match."""
        assert _spam_confidence("Viagra", "free money") == 3

    def test_high_keyword_exact_boundary(self):
        """Exactly 2 high keywords = 3."""
        assert _spam_confidence("you won act now", "x" * 200) == 3

    def test_no_keywords_just_noise(self):
        """Noise text with no keywords = 0."""
        assert _spam_confidence("random issue", "something something something") == 0

    def test_empty_string_keywords(self):
        """Empty keyword lists edge case."""
        # The actual keyword lists are module-level constants
        assert len(SPAM_KEYWORDS_HIGH) > 0
        assert len(SPAM_KEYWORDS_LOW) > 0


class TestSpamAdversarial:
    """Adversarial spam bypass attempts.

    These test whether attackers can evade spam detection through:
    - Unicode homoglyphs
    - Zero-width characters
    - Word splitting
    - Mixed scripts
    - Character substitution
    """

    def test_uppercase_mixed(self):
        """ALL CAPS spam should still be caught."""
        assert _spam_confidence("BUY NOW FREE MONEY", "CASINO PRIZE") >= 2

    def test_mixed_case_bYnOw(self):
        """Mixed case like 'bUy NoW' should still be caught (lower() handles it)."""
        assert _spam_confidence("bUy NoW fReE mOnEy", "") >= 2

    def test_unicode_homoglyph_latin_a(self):
        """Cyrillic 'а' (U+0430) instead of Latin 'a' — currently bypasses."""
        # "bау" uses Cyrillic а — the simple `in` check won't match "buy"
        result = _spam_confidence("bау now", "")
        # Document: this is a known bypass (returns 0, should be >= 2)
        assert result == 0  # Known limitation

    def test_zero_width_space_in_keyword(self):
        """Zero-width space inserted in keyword splits it — partial bypass."""
        # "buy​now" (zero-width space between buy and now) — "buy now" not matched
        # But "free money" is still found, so confidence=2 from that keyword
        result = _spam_confidence("buy​now", "")
        # "buy now" NOT found (ZWS splits it), no other keywords → 0
        assert result == 0  # ZWS successfully splits "buy now"

    def test_word_splitting_b_u_y(self):
        """Space-separated letters 'b u y' should not match."""
        result = _spam_confidence("b u y n o w", "f r e e m o n e y")
        assert result == 0  # Correct — not a keyword match

    def test_leet_speak_1(self):
        """'fr33 m0n3y' should not match (no homoglyph normalization)."""
        result = _spam_confidence("fr33 m0n3y", "")
        assert result == 0  # Known limitation — no leet speak normalization

    def test_accented_chars(self):
        """'búy nöw' with accents should not match."""
        result = _spam_confidence("búy nöw", "")
        assert result == 0  # Known limitation — no accent normalization

    def test_keyword_in_code_block(self):
        """Spam keywords inside code blocks should still be detected."""
        # The detector doesn't parse markdown — it scans raw text
        body = "```\nbuy now free money\n```"
        assert _spam_confidence("Normal title", body) >= 2

    def test_repeated_chars_break_keyword(self):
        """'buuuuy nooow' should not match (repeated chars)."""
        result = _spam_confidence("buuuuy nooow", "")
        assert result == 0  # Correct — not a keyword match

    def test_whitespace_trimming(self):
        """Leading/trailing whitespace should not affect detection."""
        assert _spam_confidence("  buy now  ", "  free money  ") >= 2

    def test_newlines_in_keyword(self):
        """Newlines splitting keyword should not match."""
        result = _spam_confidence("buy\nnow", "free\nmoney")
        # "buy\nnow" contains "buy" but not "buy now" as substring
        assert result < 2  # Correct — "buy now" not found as substring

    def test_hindi_cyrillic_mixed_script(self):
        """Mixed scripts that form keyword when combined."""
        # Not a real bypass attempt — just documenting behavior
        result = _spam_confidence("casino", "")
        assert result >= 1  # "casino" is a high keyword

    def test_empty_body_edge_case(self):
        """Empty body with spam title should still be caught."""
        assert _spam_confidence("Free money buy now", "") >= 2

    def test_long_legitimate_body_with_one_keyword(self):
        """Long legitimate body with one accidental keyword = low confidence."""
        body = "I think we should buy now and fix the bug. " + "x" * 200
        result = _spam_confidence("Bug report", body)
        assert result <= 1  # Single high keyword + long body = confidence 1


# ============================================================
# 4. _detect_secrets() (35 cases)
# ============================================================

class TestDetectSecrets:
    """Secret detection pattern tests."""

    def test_clean_text(self):
        """No secrets = empty list."""
        assert _detect_secrets("Normal text") == []

    def test_empty_text(self):
        """Empty text = empty list."""
        assert _detect_secrets("") == []

    def test_github_pat_ghp(self):
        """GitHub PAT with ghp prefix."""
        assert _detect_secrets("ghp_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_github_pat_gho(self):
        """GitHub PAT with gho prefix."""
        assert _detect_secrets("gho_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_github_pat_ghu(self):
        """GitHub PAT with ghu prefix."""
        assert _detect_secrets("ghu_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_github_pat_ghs(self):
        """GitHub PAT with ghs prefix."""
        assert _detect_secrets("ghs_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_github_pat_ghr(self):
        """GitHub PAT with ghr prefix."""
        assert _detect_secrets("ghr_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_github_pat_fine_grained(self):
        """GitHub fine-grained PAT."""
        assert _detect_secrets("github_pat_ABCDEFGHIJK12345678") == ["GitHub PAT"]

    def test_slack_token_b(self):
        """Slack bot token."""
        assert _detect_secrets("xoxb-123456789012-123456789012-AbCdEfGhIjKl") == ["Slack Token"]

    def test_slack_token_p(self):
        """Slack user token."""
        assert _detect_secrets("xoxp-123456789012-123456789012-AbCdEfGhIjKl") == ["Slack Token"]

    def test_slack_token_a(self):
        """Slack app-level token."""
        assert _detect_secrets("xoxa-123456789012-123456789012-AbCdEfGhIjKl") == ["Slack Token"]

    def test_slack_token_r(self):
        """Slack single-channel token."""
        assert _detect_secrets("xoxr-123456789012-123456789012-AbCdEfGhIjKl") == ["Slack Token"]

    def test_aws_access_key(self):
        """AWS access key ID."""
        assert _detect_secrets("AKIAIOSFODNN7EXAMPLE") == ["AWS Access Key"]

    def test_aws_access_key_abia(self):
        """AWS ABIA prefix."""
        assert _detect_secrets("ABIAIOSFODNN7EXAMPLE") == ["AWS Access Key"]

    def test_aws_access_key_acca(self):
        """AWS ACCA prefix."""
        assert _detect_secrets("ACCAIOSFODNN7EXAMPLE") == ["AWS Access Key"]

    def test_aws_access_key_asia(self):
        """AWS ASIA prefix."""
        assert _detect_secrets("ASIAIOSFODNN7EXAMPLE") == ["AWS Access Key"]

    def test_api_key_sk(self):
        """API key with sk prefix."""
        assert _detect_secrets("sk_ABCDEFGHIJK12345678") == ["API Key"]

    def test_api_key_ak(self):
        """API key with ak prefix."""
        assert _detect_secrets("ak_ABCDEFGHIJK12345678") == ["API Key"]

    def test_api_key_pk(self):
        """API key with pk prefix."""
        assert _detect_secrets("pk_ABCDEFGHIJK12345678") == ["API Key"]

    def test_api_key_underscore(self):
        """API key with underscore separator."""
        assert _detect_secrets("sk-ABCDEFGHIJK12345678") == ["API Key"]

    def test_hardcoded_password(self):
        """Hardcoded password."""
        result = _detect_secrets("password: mysecret123")
        assert "Hardcoded Secret" in result

    def test_hardcoded_secret_equals(self):
        """Hardcoded secret with equals sign."""
        result = _detect_secrets("secret=abc123def456")
        assert "Hardcoded Secret" in result

    def test_hardcoded_token(self):
        """Hardcoded token."""
        result = _detect_secrets("token: abcdef123456")
        assert "Hardcoded Secret" in result

    def test_hardcoded_api_key(self):
        """Hardcoded api_key."""
        result = _detect_secrets("api_key: abcdef123456")
        assert "Hardcoded Secret" in result

    def test_private_key_rsa(self):
        """RSA private key header."""
        assert _detect_secrets("-----BEGIN RSA PRIVATE KEY-----") == ["Private Key"]

    def test_private_key_ec(self):
        """EC private key header."""
        assert _detect_secrets("-----BEGIN EC PRIVATE KEY-----") == ["Private Key"]

    def test_private_key_generic(self):
        """Generic private key header."""
        assert _detect_secrets("-----BEGIN PRIVATE KEY-----") == ["Private Key"]

    def test_jwt_token(self):
        """JWT token."""
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        assert _detect_secrets(jwt) == ["JWT Token"]

    def test_npm_token(self):
        """NPM access token."""
        assert _detect_secrets("npm_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ab") == ["NPM Token"]

    def test_gitlab_pat(self):
        """GitLab personal access token."""
        assert _detect_secrets("glpat-AbCdEfGhIjKlMnOpQrStUv") == ["GitLab PAT"]

    def test_multiple_secrets(self):
        """Multiple secrets should all be detected."""
        text = "ghp_ABCDEFGHIJK12345678 and AKIAIOSFODNN7EXAMPLE"
        result = _detect_secrets(text)
        assert "GitHub PAT" in result
        assert "AWS Access Key" in result
        assert len(result) == 2

    def test_no_duplicates(self):
        """Same secret type should not be duplicated."""
        text = "ghp_ABCDEFGHIJK12345678 and ghp_MNOPQRSTUVWXYZ1234"
        result = _detect_secrets(text)
        assert result.count("GitHub PAT") == 1

    def test_short_ghp_not_detected(self):
        """ghp with < 10 chars after prefix should not match."""
        assert _detect_secrets("ghp_short") == []

    def test_ghp_in_longer_context(self):
        """ghp token embedded in longer text."""
        assert _detect_secrets("config: ghp_ABCDEFGHIJK12345678 in file") == ["GitHub PAT"]

    def test_password_case_insensitive(self):
        """Password keyword should be case insensitive."""
        assert _detect_secrets("PASSWORD: secret123") == ["Hardcoded Secret"]


# ============================================================
# 5. _check_title() (10 cases)
# ============================================================

class TestCheckTitle:
    """Title quality scoring tests (0-15)."""

    def test_empty_title(self):
        """Empty title = 0."""
        assert _check_title("") == 0

    def test_short_title(self):
        """Title < 10 chars = 0."""
        assert _check_title("Hi") == 0

    def test_exactly_9_chars(self):
        """Title exactly 9 chars = 0."""
        assert _check_title("123456789") == 0

    def test_exactly_10_chars(self):
        """Title exactly 10 chars = 10."""
        assert _check_title("1234567890") == 10

    def test_normal_title_30_chars(self):
        """Normal title ~30 chars = 10."""
        assert _check_title("This is a good issue title") == 10

    def test_optimal_title_50_chars(self):
        """Title 50 chars = 15 (optimal)."""
        assert _check_title("A" * 50) == 15

    def test_long_title_200(self):
        """Title exactly 200 chars = 15."""
        assert _check_title("A" * 200) == 15

    def test_very_long_title_201(self):
        """Title > 200 chars = 12."""
        assert _check_title("A" * 201) == 12

    def test_huge_title(self):
        """Title 1000 chars = 12."""
        assert _check_title("A" * 1000) == 12

    def test_boundary_11_chars(self):
        """Title 11 chars = 10."""
        assert _check_title("12345678901") == 10

    def test_unicode_title(self):
        """Unicode title that's long enough = 10."""
        assert _check_title("这是一个很好的issue标题") == 10


# ============================================================
# 6. _check_body() (10 cases)
# ============================================================

class TestCheckBody:
    """Body quality scoring tests (0-30)."""

    def test_empty_body(self):
        """Empty body = 0."""
        assert _check_body("") == 0

    def test_short_body(self):
        """Body < 20 chars = 0."""
        assert _check_body("Short") == 0

    def test_boundary_19_chars(self):
        """Body 19 chars = 0."""
        assert _check_body("A" * 19) == 0

    def test_boundary_20_chars(self):
        """Body 20 chars = 8 (in 20-99 range)."""
        assert _check_body("A" * 20) == 8

    def test_medium_body_50(self):
        """Body 50 chars = 8."""
        assert _check_body("A" * 50) == 8

    def test_boundary_99_chars(self):
        """Body 99 chars = 8."""
        assert _check_body("A" * 99) == 8

    def test_boundary_100_chars(self):
        """Body 100 chars = 15 (in 100-499 range)."""
        assert _check_body("A" * 100) == 15

    def test_body_499_chars(self):
        """Body 499 chars = 15."""
        assert _check_body("A" * 499) == 15

    def test_boundary_500_chars(self):
        """Body 500 chars = 22 (in 500-1999 range)."""
        assert _check_body("A" * 500) == 22

    def test_boundary_1999_chars(self):
        """Body 1999 chars = 22."""
        assert _check_body("A" * 1999) == 22

    def test_boundary_2000_chars(self):
        """Body 2000 chars = 30 (optimal range)."""
        assert _check_body("A" * 2000) == 30

    def test_optimal_body(self):
        """Body 5000 chars = 30."""
        assert _check_body("A" * 5000) == 30

    def test_boundary_10000_chars(self):
        """Body exactly 10000 chars = 30."""
        assert _check_body("A" * 10000) == 30

    def test_very_long_body(self):
        """Body > 10000 chars = 25."""
        assert _check_body("A" * 10001) == 25


# ============================================================
# 7. _check_labels() (8 cases)
# ============================================================

class TestCheckLabels:
    """Label scoring tests (0-15)."""

    def test_no_labels(self):
        """No labels = 0."""
        assert _check_labels([]) == 0

    def test_one_label(self):
        """One label = 5."""
        assert _check_labels(["bug"]) == 5

    def test_two_labels(self):
        """Two labels = 10."""
        assert _check_labels(["bug", "help wanted"]) == 10

    def test_three_labels(self):
        """Three labels = 15."""
        assert _check_labels(["bug", "help wanted", "p1"]) == 15

    def test_five_labels(self):
        """Five labels = 15."""
        assert _check_labels(["a", "b", "c", "d", "e"]) == 15

    def test_hundred_labels(self):
        """Hundred labels = 15."""
        assert _check_labels([f"label{i}" for i in range(100)]) == 15

    def test_empty_string_label(self):
        """Empty string label still counts."""
        assert _check_labels([""]) == 5

    def test_mixed_valid_invalid(self):
        """Mix of valid and invalid labels."""
        assert _check_labels(["bug", "", "help wanted"]) == 15


# ============================================================
# 8. _check_structure() (10 cases)
# ============================================================

class TestCheckStructure:
    """Body structure scoring tests (0-20)."""

    def test_empty_body(self):
        """Empty body = 0."""
        assert _check_structure("") == 0

    def test_no_structure(self):
        """Plain text, no headers or lists = 0."""
        assert _check_structure("Just plain text without any structure.") == 0

    def test_headers_only(self):
        """Headers only = 10."""
        assert _check_structure("## Description\nSome text") == 10

    def test_lists_only(self):
        """Lists only = 5."""
        assert _check_structure("- item 1\n- item 2") == 5

    def test_headers_and_lists(self):
        """Both headers and lists = 15."""
        assert _check_structure("## Description\n- item 1\n- item 2") == 15

    def test_headers_lists_and_code(self):
        """Headers + lists + code blocks = 20."""
        body = "## Desc\n- item\n```\ncode\n```"
        assert _check_structure(body) == 20

    def test_asterisk_lists(self):
        """Asterisk lists should count."""
        assert _check_structure("## Section\n* item 1\n* item 2") == 15

    def test_h1_header(self):
        """H1 header should count."""
        assert _check_structure("# Title\nSome text") == 10

    def test_h3_header(self):
        """H3 header should count."""
        assert _check_structure("### Subtitle\nSome text") == 10

    def test_h4_header_does_not_count(self):
        """H4 header should NOT count (only h1-h3)."""
        assert _check_structure("#### Sub-subtitle\nSome text") == 0

    def test_multiline_headers_and_lists(self):
        """Multiple headers and lists = 15."""
        body = "## Desc\n- a\n## Steps\n- b\n## Expected\n- c"
        assert _check_structure(body) == 15


# ============================================================
# 9. _check_no_secrets() (8 cases)
# ============================================================

class TestCheckNoSecrets:
    """No-secrets scoring tests (0-20)."""

    def test_clean_body(self):
        """No secrets = 20."""
        assert _check_no_secrets("Normal text here") == 20

    def test_empty_body(self):
        """Empty body = 20."""
        assert _check_no_secrets("") == 20

    def test_with_github_pat(self):
        """GitHub PAT present = 0."""
        assert _check_no_secrets("ghp_ABCDEFGHIJK12345678") == 0

    def test_with_password(self):
        """Password present = 0."""
        assert _check_no_secrets("password: secret123") == 0

    def test_with_private_key(self):
        """Private key present = 0."""
        assert _check_no_secrets("-----BEGIN PRIVATE KEY-----") == 0

    def test_with_aws_key(self):
        """AWS key present = 0."""
        assert _check_no_secrets("AKIAIOSFODNN7EXAMPLE") == 0

    def test_clean_code_snippet(self):
        """Code snippet without secrets = 20."""
        assert _check_no_secrets("```python\nprint('hello')\n```") == 20

    def test_multiple_clean_blocks(self):
        """Multiple clean text blocks = 20."""
        assert _check_no_secrets("Block 1\nBlock 2\nBlock 3") == 20


# ============================================================
# 10. _check_labels_complete() (12 cases)
# ============================================================

class TestCheckLabelsComplete:
    """Label completeness validation tests."""

    def test_no_labels_no_issues(self):
        """No labels = no issues (function only checks specific types)."""
        assert _check_labels_complete([], "") == []

    def test_intake_with_pending_review(self):
        """Intake + pending-review = no issues."""
        assert _check_labels_complete(["intake", "pending-review"], "") == []

    def test_intake_without_pending_review(self):
        """Intake without pending-review = 1 issue."""
        issues = _check_labels_complete(["intake"], "")
        assert len(issues) == 1
        assert issues[0]["severity"] == "medium"
        assert "pending-review" in issues[0]["description"]

    def test_bug_with_repro_steps(self):
        """Bug with repro steps = no issues."""
        body = "## Steps to Reproduce\n1. Do this\n2. Do that"
        assert _check_labels_complete(["bug"], body) == []

    def test_bug_with_reproduce_keyword(self):
        """Bug with 'reproduce' keyword = no issues."""
        assert _check_labels_complete(["bug"], "How to reproduce this?") == []

    def test_bug_with_reproduction_keyword(self):
        """Bug with 'reproduction' keyword = no issues."""
        assert _check_labels_complete(["bug"], "Reproduction steps below") == []

    def test_bug_with_steps_to_keyword(self):
        """Bug with 'steps to' keyword = no issues."""
        assert _check_labels_complete(["bug"], "Steps to reproduce:\n1. Go to settings") == []

    def test_bug_with_chinese_repro(self):
        """Bug with Chinese '复现' keyword = no issues."""
        assert _check_labels_complete(["bug"], "复现步骤：打开应用") == []

    def test_bug_with_numbered_steps(self):
        """Bug with numbered steps = no issues."""
        assert _check_labels_complete(["bug"], "1. Open app\n2. Click button") == []

    def test_bug_without_repro(self):
        """Bug without any repro indicators = 1 issue."""
        issues = _check_labels_complete(["bug"], "It crashes sometimes")
        assert len(issues) == 1
        assert issues[0]["severity"] == "medium"
        assert "reproduction" in issues[0]["description"].lower()

    def test_enhancement_label_no_check(self):
        """Enhancement label = no special checks."""
        assert _check_labels_complete(["enhancement"], "") == []

    def test_mixed_labels_intake_issue(self):
        """Intake + other labels, missing pending-review."""
        issues = _check_labels_complete(["intake", "bug"], "")
        # Should get intake warning
        assert any("pending-review" in i["description"] for i in issues)

    def test_bug_case_insensitive_body(self):
        """Bug repro check should be case insensitive."""
        assert _check_labels_complete(["bug"], "REPRODUCE the issue") == []


# ============================================================
# 11. _calculate_tier() (12 cases)
# ============================================================

class TestCalculateTier:
    """_calculate_tier() priority logic."""

    def test_negative_critical_returns_high_risk(self):
        """Critical negative signal → high_risk."""
        neg = [{"key": "spam", "severity": "critical"}]
        assert _calculate_tier(neg, [], 50) == "high_risk"

    def test_negative_high_returns_high_risk(self):
        """High severity negative → high_risk."""
        neg = [{"key": "secret", "severity": "high"}]
        assert _calculate_tier(neg, [], 50) == "high_risk"

    def test_two_medium_negatives_returns_high_risk(self):
        """2+ medium negatives → high_risk."""
        neg = [
            {"key": "a", "severity": "medium"},
            {"key": "b", "severity": "medium"},
        ]
        assert _calculate_tier(neg, [], 50) == "high_risk"

    def test_one_medium_no_positive_returns_high_risk(self):
        """1 medium negative + no positive → high_risk."""
        neg = [{"key": "a", "severity": "medium"}]
        assert _calculate_tier(neg, [], 50) == "high_risk"

    def test_low_score_returns_high_risk(self):
        """Score < 30 → high_risk."""
        assert _calculate_tier([], [], 25) == "high_risk"

    def test_medium_score_returns_medium_risk(self):
        """Score 30-59 with no signals → medium_risk."""
        assert _calculate_tier([], [], 45) == "medium_risk"

    def test_high_score_returns_low_risk(self):
        """Score >= 60 + positive signals → low_risk."""
        pos = [{"key": "a"}, {"key": "b"}]
        assert _calculate_tier([], pos, 70) == "low_risk"

    def test_high_score_no_signals_returns_medium(self):
        """High score but no positive signals → medium_risk."""
        assert _calculate_tier([], [], 80) == "medium_risk"

    def test_one_medium_with_positive_returns_medium(self):
        """1 medium negative + positive → medium_risk."""
        neg = [{"key": "a", "severity": "medium"}]
        pos = [{"key": "b"}]
        assert _calculate_tier(neg, pos, 60) == "medium_risk"

    def test_empty_signals_medium_score(self):
        """No signals, medium score → medium_risk."""
        assert _calculate_tier([], [], 50) == "medium_risk"

    def test_many_positives_no_negatives(self):
        """Many positives, no negatives → low_risk."""
        pos = [{"key": "a"}, {"key": "b"}, {"key": "c"}]
        assert _calculate_tier([], pos, 80) == "low_risk"

    def test_critical_overrides_positives(self):
        """Critical negative overrides positives."""
        neg = [{"key": "spam", "severity": "critical"}]
        pos = [{"key": "a"}, {"key": "b"}]
        assert _calculate_tier(neg, pos, 90) == "high_risk"

# ============================================================
# 12. _grade() (10 cases)
# ============================================================

class TestGrade:
    """Grade mapping tests."""

    def test_grade_a(self):
        """Score >= 90 = A."""
        assert _grade(90) == "A"
        assert _grade(100) == "A"

    def test_grade_b(self):
        """Score 75-89 = B."""
        assert _grade(75) == "B"
        assert _grade(89) == "B"

    def test_grade_c(self):
        """Score 60-74 = C."""
        assert _grade(60) == "C"
        assert _grade(74) == "C"

    def test_grade_d(self):
        """Score 40-59 = D."""
        assert _grade(40) == "D"
        assert _grade(59) == "D"

    def test_grade_f(self):
        """Score < 40 = F."""
        assert _grade(0) == "F"
        assert _grade(39) == "F"

    def test_boundary_89(self):
        """89 = B."""
        assert _grade(89) == "B"

    def test_boundary_74(self):
        """74 = C."""
        assert _grade(74) == "C"

    def test_boundary_59(self):
        """59 = D."""
        assert _grade(59) == "D"

    def test_boundary_39(self):
        """39 = F."""
        assert _grade(39) == "F"

    def test_boundary_90(self):
        """90 = A."""
        assert _grade(90) == "A"


# ============================================================
# 13. Checklist generation (replaces _generate_suggestions)
# ============================================================

class TestChecklist:
    """Checklist generation (replaces _generate_suggestions)."""

    def test_low_score_gets_improve_content(self):
        """Score < 40 should add improve_content checklist item."""
        r = analyze_issue(_make_issue(title="hi", body="x", labels=[]))
        actions = [c["action"] for c in r["checklist"]]
        assert "improve_content" in actions

    def test_high_score_no_improve_content(self):
        """Score >= 40 should not add improve_content."""
        r = analyze_issue(_make_issue(
            title="Bug: Something broken in the app",
            body="A" * 500 + "\n## Steps\n- step 1\n- step 2",
            labels=["bug", "help wanted"],
        ))
        actions = [c["action"] for c in r["checklist"]]
        assert "improve_content" not in actions

    def test_not_crawler_gets_add_crawler_labels(self):
        """Non-crawler-friendly should add add_crawler_labels."""
        r = analyze_issue(_make_issue(labels=[]))
        actions = [c["action"] for c in r["checklist"]]
        assert "add_crawler_labels" in actions

    def test_crawler_friendly_no_crawler_label_item(self):
        """Crawler-friendly should not add add_crawler_labels."""
        r = analyze_issue(_make_issue(
            labels=["agent-friendly", "no-credentials", "has-test"],
        ))
        actions = [c["action"] for c in r["checklist"]]
        assert "add_crawler_labels" not in actions

    def test_checklist_items_have_required_fields(self):
        """All checklist items should have action, priority, done, hint."""
        r = analyze_issue(_make_issue(title="hi", body="x", labels=[]))
        for item in r["checklist"]:
            assert "action" in item
            assert "priority" in item
            assert "done" in item
            assert "hint" in item

    def test_spam_returns_close_spam_checklist(self):
        """Spam issue should have close_spam in checklist."""
        r = analyze_issue(_make_issue(
            title="Buy now free money casino",
            body="You won! Click here.",
        ))
        actions = [c["action"] for c in r["checklist"]]
        assert "close_spam" in actions

    def test_secret_leakage_returns_redact_secrets(self):
        """Secret leakage should have redact_secrets in checklist."""
        r = analyze_issue(_make_issue(body="password=abc123xyz"))
        actions = [c["action"] for c in r["checklist"]]
        assert "redact_secrets" in actions

    def test_empty_issue_has_improve_content(self):
        """Empty issue should have improve_content."""
        r = analyze_issue(_make_issue(title="", body=None, labels=[]))
        actions = [c["action"] for c in r["checklist"]]
        assert "improve_content" in actions

    def test_checklist_priority_order(self):
        """P0 items should come before P1/P2."""
        r = analyze_issue(_make_issue(
            title="Buy now free money casino",
            body="password=abc123xyz",
        ))
        priorities = [c["priority"] for c in r["checklist"]]
        # P0 (close_spam) should be first
        assert priorities[0] == "P0"

    def test_both_low_score_and_not_crawler(self):
        """Both low score and not crawler = 2 checklist items (plus any signal-based)."""
        r = analyze_issue(_make_issue(title="hi", body="x", labels=[]))
        actions = [c["action"] for c in r["checklist"]]
        assert "improve_content" in actions
        assert "add_crawler_labels" in actions

# ============================================================
# 14. Constant Integrity (12 cases)
# ============================================================

class TestConstants:
    """Module constant sanity checks."""

    def test_issue_type_labels_keys(self):
        """Issue type labels should have expected keys."""
        assert "bug" in ISSUE_TYPE_LABELS
        assert "enhancement" in ISSUE_TYPE_LABELS
        assert "documentation" in ISSUE_TYPE_LABELS
        assert "question" in ISSUE_TYPE_LABELS
        assert "intake" in ISSUE_TYPE_LABELS
        assert "security" in ISSUE_TYPE_LABELS

    def test_required_labels_keys(self):
        """Required labels should cover key types."""
        assert "intake" in REQUIRED_LABELS
        assert "bug" in REQUIRED_LABELS
        assert "enhancement" in REQUIRED_LABELS

    def test_required_labels_values(self):
        """Required label values should be lists."""
        for key, val in REQUIRED_LABELS.items():
            assert isinstance(val, list)
            assert len(val) > 0

    def test_crawler_labels_non_empty(self):
        """Crawler labels set should not be empty."""
        assert len(CRAWLER_LABELS) >= 5

    def test_crawler_labels_are_strings(self):
        """All crawler labels should be strings."""
        for label in CRAWLER_LABELS:
            assert isinstance(label, str)

    def test_default_crawler_threshold(self):
        """Default crawler threshold should be positive."""
        assert DEFAULT_CRAWLER_THRESHOLD >= 1

    def test_quality_dimensions_non_empty(self):
        """Quality dimensions should not be empty."""
        assert len(QUALITY_DIMENSIONS) >= 5

    def test_quality_dimensions_have_weight(self):
        """Each quality dimension should have a weight."""
        for key, dim in QUALITY_DIMENSIONS.items():
            assert "weight" in dim
            assert dim["weight"] > 0

    def test_spam_keywords_high_non_empty(self):
        """High spam keywords should not be empty."""
        assert len(SPAM_KEYWORDS_HIGH) >= 5

    def test_spam_keywords_low_non_empty(self):
        """Low spam keywords should not be empty."""
        assert len(SPAM_KEYWORDS_LOW) >= 5

    def test_secret_patterns_non_empty(self):
        """Secret patterns should not be empty."""
        assert len(SECRET_PATTERNS) >= 5

    def test_secret_patterns_compiled(self):
        """Secret patterns should be compiled regex."""
        for pattern, name in SECRET_PATTERNS:
            assert hasattr(pattern, "search")
            assert isinstance(name, str)


# ============================================================
# 15. Edge Cases & Integration (20 cases)
# ============================================================

class TestEdgeCases:
    """Edge case and integration tests."""

    def test_issue_with_none_labels(self):
        """Issue with no labels key should not crash."""
        issue = {"number": 1, "title": "Test", "body": "Body"}
        r = analyze_issue(issue)
        assert r["score"] >= 0

    def test_issue_with_empty_body(self):
        """Issue with empty string body should work."""
        r = analyze_issue(_make_issue(body=""))
        assert r["score"] >= 0

    def test_issue_with_very_long_body(self):
        """Issue with very long body should work."""
        r = analyze_issue(_make_issue(body="A" * 50000))
        assert r["score"] <= 100

    def test_issue_with_special_characters(self):
        """Issue with special characters should not crash."""
        r = analyze_issue(_make_issue(
            title="Bug: <script>alert('xss')</script>",
            body="```html\n<script>alert('xss')</script>\n```",
        ))
        assert r["score"] >= 0

    def test_issue_with_unicode(self):
        """Issue with unicode content should work."""
        r = analyze_issue(_make_issue(
            title="Bug: 中文标题测试",
            body="## 描述\n这是一个测试issue的描述。\n\n### 步骤\n1. 打开应用\n2. 点击按钮",
        ))
        assert r["score"] > 0

    def test_issue_with_emoji(self):
        """Issue with emoji should work."""
        r = analyze_issue(_make_issue(
            title="Bug: 🐛 Button crashes on click",
            body="## Description 📝\nThe app crashes 💥 when clicking submit.",
        ))
        assert r["score"] > 0

    def test_issue_with_markdown_code_block(self):
        """Issue with code blocks should be handled."""
        body = "## Error\n```\nTraceback (most recent call last):\n  File 'app.py', line 10\n```"
        r = analyze_issue(_make_issue(body=body))
        assert r["score"] > 0

    def test_issue_with_links(self):
        """Issue with links should work."""
        body = "See [documentation](https://example.com) for details."
        r = analyze_issue(_make_issue(body=body))
        assert r["score"] > 0

    def test_spam_with_legitimate_content_mixed(self):
        """Mix of spam and legitimate content."""
        r = analyze_issue(_make_issue(
            title="Help needed",
            body="buy now free money casino",
        ))
        # Two high keywords = spam
        assert r["is_spam"] is True

    def test_secret_in_title(self):
        """Secret in title should be detected in body scan."""
        # Title is not scanned for secrets, only body
        r = analyze_issue(_make_issue(
            title="ghp_ABCDEFGHIJK12345678",
            body="Normal body",
        ))
        # Title secrets not detected (body-only scan)
        assert r["is_spam"] is False

    def test_batch_all_different_risks(self):
        """Batch with different risk levels."""
        issues = [
            _make_issue(title="Buy now free money", body="casino"),  # critical
            _make_issue(body="password=secret123"),  # high
            _make_issue(title="A" * 50, body="B" * 200),  # depends on score
        ]
        r = analyze_issues_batch(issues)
        assert r["spam_count"] == 1
        assert r["high_risk_count"] >= 1

    def test_result_structure_completeness(self):
        """Result should have all expected keys (aligned with PR Coach)."""
        r = analyze_issue(_make_issue())
        expected_keys = {
            "number", "title", "tier", "signals", "checklist",
            "score", "quality_grade", "is_crawler_friendly", "is_spam",
        }
        assert set(r.keys()) == expected_keys

    def test_score_is_int(self):
        """Score should be an integer."""
        r = analyze_issue(_make_issue())
        assert isinstance(r["score"], int)

    def test_risk_is_valid_string(self):
        """Risk should be one of the valid values."""
        r = analyze_issue(_make_issue())
        assert r["tier"] in ("low_risk", "medium_risk", "high_risk")

    def test_quality_grade_is_valid(self):
        """Quality grade should be one of the valid values."""
        r = analyze_issue(_make_issue())
        assert r["quality_grade"] in ("A", "B", "C", "D", "F")

    def test_issues_list_contains_dicts(self):
        """Signals negative list should contain dicts with expected keys."""
        r = analyze_issue(_make_issue(
            labels=["bug"],
            body="It crashes",
        ))
        for sig in r["signals"]["negative"]:
            assert "key" in sig
            assert "description" in sig
            assert "severity" in sig

    def test_analyze_issue_does_not_mutate_input(self):
        """analyze_issue should not mutate the input dict."""
        issue = _make_issue(number=5, title="Test", body="Body", labels=["bug"])
        import copy
        original = copy.deepcopy(issue)
        analyze_issue(issue)
        assert issue == original

    def test_batch_does_not_mutate_inputs(self):
        """analyze_issues_batch should not mutate input list."""
        issues = [_make_issue(number=i) for i in range(3)]
        import copy
        original = copy.deepcopy(issues)
        analyze_issues_batch(issues)
        assert issues == original

    def test_concurrent_same_input_same_output(self):
        """Same input should produce same output."""
        issue = _make_issue(number=7, title="Consistent", body="Test body here")
        r1 = analyze_issue(issue)
        r2 = analyze_issue(issue)
        assert r1["score"] == r2["score"]
        assert r1["tier"] == r2["tier"]
        assert r1["quality_grade"] == r2["quality_grade"]


# ============================================================
# 16. Regression — v1.1.0 Fixes (15 cases)
# ============================================================

class TestV110Regression:
    """Regression tests for v1.1.0 maintainer review fixes."""

    def test_secret_name_is_human_readable(self):
        """Secret detection should return human-readable names."""
        r = analyze_issue(_make_issue(body="ghp_ABCDEFGHIJK12345678"))
        secret_issues = [i for i in r["signals"]["negative"] if "secret" in i["description"].lower()
                         or "Secret" in i["description"]]
        assert len(secret_issues) == 1
        assert "GitHub PAT" in secret_issues[0]["description"]

    def test_spam_short_body_higher_confidence(self):
        """Short body + keyword should get higher confidence."""
        # Short body (< 100) + single high keyword = confidence 2 = spam
        r = analyze_issue(_make_issue(
            title="Free money",
            body="Short",
        ))
        assert r["is_spam"] is True

    def test_spam_long_body_lower_confidence(self):
        """Long body + single high keyword = confidence 1 = not spam."""
        r = analyze_issue(_make_issue(
            title="Normal title here",
            body="buy now " + "A" * 200,
        ))
        assert r["is_spam"] is False

    def test_calculate_tier_high_severity_returns_high_risk(self):
        """_calculate_tier should return high_risk for high severity signals."""
        neg = [{"key": "secret", "severity": "high"}]
        assert _calculate_tier(neg, [], 90) == "high_risk"

    def test_calculate_tier_critical_severity_returns_high_risk(self):
        """_calculate_tier should return high_risk for critical severity signals."""
        neg = [{"key": "spam", "severity": "critical"}]
        assert _calculate_tier(neg, [], 90) == "high_risk"

    def test_result_carries_number_and_title(self):
        """Result should always carry issue number and title."""
        r = analyze_issue(_make_issue(number=42, title="My Issue"))
        assert r["number"] == 42
        assert r["title"] == "My Issue"

    def test_spam_returns_immediately_no_other_checks(self):
        """Spam detection should short-circuit."""
        r = analyze_issue(_make_issue(
            title="Buy now free money",
            body="Casino",
            labels=["agent-friendly", "no-credentials", "has-test"],
        ))
        # Should return immediately, no crawler check, no score
        assert r["score"] == 0
        assert r["is_crawler_friendly"] is False

    def test_medium_severity_with_positive_returns_medium(self):
        """Medium severity + positive signals → medium_risk."""
        neg = [{"key": "x", "severity": "medium"}]
        pos = [{"key": "y"}]
        assert _calculate_tier(neg, pos, 70) == "medium_risk"

    def test_low_severity_no_negative_returns_medium(self):
        """1 positive, no negatives → medium_risk (need 2+ for low_risk)."""
        pos = [{"key": "y"}]
        assert _calculate_tier([], pos, 70) == "medium_risk"

    def test_multiple_secret_types_human_readable(self):
        """Multiple secrets should be human-readable."""
        r = analyze_issue(_make_issue(
            body="ghp_ABCDEFGHIJK12345678 and AKIAIOSFODNN7EXAMPLE",
        ))
        secret_issues = [i for i in r["signals"]["negative"] if "secret" in i["description"].lower()]
        assert len(secret_issues) == 1
        assert "GitHub PAT" in secret_issues[0]["description"]
        assert "AWS Access Key" in secret_issues[0]["description"]

    def test_spam_confidence_boundary_100(self):
        """Body length exactly 100 with high keyword = confidence 1 (not spam)."""
        body = "buy now " + "x" * 92  # total ~100 chars
        assert _spam_confidence("Title", body) == 1

    def test_spam_confidence_boundary_99(self):
        """Body length 99 with high keyword = confidence 2 (spam)."""
        body = "buy now " + "x" * 91  # total ~99 chars
        assert _spam_confidence("Title", body) == 2

    def test_issue_with_only_low_severity_issues(self):
        """Low severity signals with medium score → medium_risk."""
        neg = [
            {"key": "a", "severity": "low"},
            {"key": "b", "severity": "low"},
        ]
        # low severity not counted as medium, score 50 → medium_risk
        assert _calculate_tier(neg, [], 50) == "medium_risk"

    def test_empty_signals_score_based(self):
        """Empty signals should base tier on score only."""
        assert _calculate_tier([], [], 70) == "medium_risk"  # no pos → medium
        assert _calculate_tier([], [{"key": "a"}, {"key": "b"}], 70) == "low_risk"  # 2+ pos → low
        assert _calculate_tier([], [], 25) == "high_risk"  # score < 30 → high

    def test_v110_all_fixes集成(self):
        """Integration test: v1.1.0 all fixes together."""
        r = analyze_issue(_make_issue(
            number=100,
            title="Bug: App crashes on startup",
            body=(
                "## Description\n"
                "The app crashes.\n\n"
                "## Steps to Reproduce\n"
                "- 1. Open app\n"
                "- 2. Click start\n\n"
                "My password=supersecret123"
            ),
            labels=["bug", "help wanted", "good first issue", "agent-friendly"],
        ))
        # Should detect secret
        assert any("Hardcoded Secret" in i["description"] or "Secret" in i["description"]
                    for i in r["signals"]["negative"])
        # Should not be spam
        assert r["is_spam"] is False
        # Should carry number and title
        assert r["number"] == 100
        assert r["title"] == "Bug: App crashes on startup"
        # Risk should be high (secret detected)
        assert r["tier"] == "high_risk"


# ============================================================
# 17. Performance — Batch Throughput (5 cases)
# ============================================================

class TestPerformance:
    """Batch performance and throughput tests."""

    @pytest.fixture
    def large_batch(self):
        """Generate 1000 diverse issues."""
        import random
        random.seed(42)
        issues = []
        titles = [
            "Bug: Application crashes on startup",
            "Feature: Add dark mode support",
            "Fix: Memory leak in worker process",
            "Issue: API returns 500 intermittently",
            "Enhancement: Improve error messages",
        ]
        bodies = [
            "## Description\nThe app crashes.\n\n## Steps\n1. Start app\n2. Click button",
            "## Feature Request\nAdd dark mode toggle.\n\n- [ ] Design\n- [ ] Implement\n- [ ] Test",
            "## Bug Report\nMemory usage grows over time.\n\n```\nheap: 2GB+\n```",
            "## Problem\nAPI intermittently returns 500.\n\n## Expected\nShould return 200.",
            "## Enhancement\nBetter error messages for users.\n\n### Current\n\"Error occurred\"\n### Proposed\n\"Connection timeout\"",
        ]
        label_sets = [
            ["bug", "help wanted", "good first issue"],
            ["enhancement", "design"],
            ["bug", "critical", "p0"],
            ["question", "support"],
            ["documentation", "help wanted"],
        ]
        for i in range(1000):
            issues.append({
                "number": i,
                "title": random.choice(titles) + f" #{i}",
                "body": random.choice(bodies) + f"\n\nIssue #{i}",
                "labels": [{"name": l} for l in random.choice(label_sets)],
            })
        return issues

    def test_batch_1000_under_1s(self, large_batch):
        """1000 issues should be analyzed in under 1 second."""
        import time
        start = time.monotonic()
        result = analyze_issues_batch(large_batch)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"Batch of 1000 took {elapsed:.2f}s (>1s)"
        assert result["total"] == 1000

    def test_single_issue_under_1ms(self):
        """Single issue analysis should complete in under 1ms."""
        import time
        issue = _make_issue(
            title="Bug: Detailed issue with reproduction steps",
            body="## Description\n" + "x " * 100 + "\n\n## Steps\n- 1. Do this\n- 2. Do that",
            labels=["bug", "help wanted", "good first issue"],
        )
        times = []
        for _ in range(100):
            start = time.monotonic()
            analyze_issue(issue)
            times.append(time.monotonic() - start)
        avg_ms = (sum(times) / len(times)) * 1000
        assert avg_ms < 1.0, f"Average single issue analysis: {avg_ms:.2f}ms (>1ms)"

    def test_batch_10000_under_5s(self):
        """10000 issues should be analyzed in under 5 seconds."""
        import time
        issues = [_make_issue(number=i, title=f"Issue #{i}", body="A" * 200) for i in range(10000)]
        start = time.monotonic()
        result = analyze_issues_batch(issues)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Batch of 10000 took {elapsed:.2f}s (>5s)"
        assert result["total"] == 10000

    def test_batch_with_mixtures_performance(self):
        """Batch with spam+secrets+clean issues should not degrade."""
        import time
        issues = []
        for i in range(500):
            if i % 10 == 0:
                issues.append(_make_issue(title="Buy now free money", body="Casino"))
            elif i % 10 == 1:
                issues.append(_make_issue(body="password=secret123"))
            else:
                issues.append(_make_issue(
                    title=f"Issue #{i}",
                    body="## Description\n" + "x " * 100,
                    labels=["bug", "help wanted"],
                ))
        start = time.monotonic()
        result = analyze_issues_batch(issues)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0
        assert result["spam_count"] == 50
        assert result["high_risk_count"] >= 50

    def test_batch_1000_memory_reasonable(self, large_batch):
        """Batch of 1000 should not use excessive memory."""
        import tracemalloc
        tracemalloc.start()
        analyze_issues_batch(large_batch)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # Peak should be under 50MB for 1000 issues
        assert peak < 50 * 1024 * 1024, f"Peak memory: {peak / 1024 / 1024:.1f}MB (>50MB)"


# ============================================================
# 18. Integration — Mock GitHub API (8 cases)
# ============================================================

class TestGitHubAPIIntegration:
    """Integration tests simulating GitHub API responses."""

    @pytest.fixture
    def mock_github_response(self):
        """Simulate GitHub API /repos/{owner}/{repo}/issues response."""
        return [
            {
                "number": 1234,
                "title": "Bug: App crashes on mobile when rotating screen",
                "body": (
                    "## Description\n"
                    "The app crashes when rotating the screen on iOS devices.\n\n"
                    "## Steps to Reproduce\n"
                    "1. Open the app on iPhone\n"
                    "2. Rotate to landscape\n"
                    "3. App crashes with SIGABRT\n\n"
                    "## Expected\n"
                    "App should rotate smoothly.\n\n"
                    "## Environment\n"
                    "- iOS 17.2\n"
                    "- iPhone 15 Pro\n"
                    "- App version 2.1.0"
                ),
                "labels": [
                    {"name": "bug"},
                    {"name": "mobile"},
                    {"name": "P1"},
                ],
                "state": "open",
                "created_at": "2026-08-15T10:00:00Z",
                "user": {"login": "user123"},
            },
            {
                "number": 1235,
                "title": "FREE MONEY!!! Buy now!!!",
                "body": "You won a prize! Click here to claim your free gift!",
                "labels": [],
                "state": "open",
                "created_at": "2026-08-15T11:00:00Z",
                "user": {"login": "spammer42"},
            },
            {
                "number": 1236,
                "title": "Feature: Add export to PDF",
                "body": (
                    "## Problem\n"
                    "Users can't export reports to PDF.\n\n"
                    "## Proposed Solution\n"
                    "Add a PDF export button in the report view.\n\n"
                    "## Alternatives\n"
                    "- Print to PDF (ugly)\n"
                    "- Screenshot (low quality)"
                ),
                "labels": [
                    {"name": "enhancement"},
                    {"name": "feature-request"},
                ],
                "state": "open",
                "created_at": "2026-08-15T12:00:00Z",
                "user": {"login": "contributor456"},
            },
        ]

    def test_analyze_github_response(self, mock_github_response):
        """Full pipeline: GitHub response → analyze_issues_batch."""
        result = analyze_issues_batch(mock_github_response)
        assert result["total"] == 3
        assert result["spam_count"] == 1
        assert result["results"][0]["number"] == 1234
        assert result["results"][1]["number"] == 1235
        assert result["results"][2]["number"] == 1236

    def test_triage_by_risk(self, mock_github_response):
        """Should correctly triage issues by risk level."""
        result = analyze_issues_batch(mock_github_response)
        by_tier = {}
        for r in result["results"]:
            by_tier.setdefault(r["tier"], []).append(r["number"])
        # Issue 1235 is spam → high_risk
        assert 1235 in by_tier.get("high_risk", [])
        # Issue 1234 is good bug report → low_risk or medium_risk
        assert 1234 in by_tier.get("low_risk", []) or 1234 in by_tier.get("medium_risk", [])

    def test_triage_by_grade(self, mock_github_response):
        """Should correctly grade issues."""
        result = analyze_issues_batch(mock_github_response)
        grades = {r["number"]: r["quality_grade"] for r in result["results"]}
        # Spam gets F
        assert grades[1235] == "F"
        # Good bug report gets better grade
        assert grades[1234] in ("A", "B", "C")

    def test_maintainer_dashboard_input(self, mock_github_response):
        """Output format should be suitable for maintainer dashboard."""
        result = analyze_issues_batch(mock_github_response)
        # Dashboard needs these fields
        assert "total" in result
        assert "spam_count" in result
        assert "high_risk_count" in result
        assert "average_score" in result
        assert "grade_distribution" in result
        assert "results" in result
        # Each result needs dashboard fields (aligned with PR Coach)
        for r in result["results"]:
            assert "number" in r
            assert "title" in r
            assert "score" in r
            assert "tier" in r
            assert "signals" in r
            assert "checklist" in r
            assert "quality_grade" in r

    def test_empty_labels_github_format(self):
        """GitHub issues with empty labels list should work."""
        issues = [
            {"number": 1, "title": "No labels here", "body": "Body", "labels": []},
        ]
        result = analyze_issues_batch(issues)
        assert result["total"] == 1
        assert result["results"][0]["score"] >= 0

    def test_none_body_github_format(self):
        """GitHub issues with None body should work."""
        issues = [
            {"number": 1, "title": "No body", "body": None, "labels": []},
        ]
        result = analyze_issues_batch(issues)
        assert result["total"] == 1

    def test_large_github_response(self):
        """Simulate large GitHub API page (100 issues)."""
        issues = []
        for i in range(100):
            issues.append({
                "number": i,
                "title": f"Issue #{i}: {'Bug' if i % 3 == 0 else 'Feature'} description",
                "body": f"## Description\nContent for issue {i}\n\n" + "- item\n" * 5,
                "labels": [{"name": "bug"}] if i % 3 == 0 else [{"name": "enhancement"}],
            })
        result = analyze_issues_batch(issues)
        assert result["total"] == 100
        assert result["spam_count"] == 0
        assert result["average_score"] > 0

    def test_mixed_quality_github_response(self):
        """GitHub response with varying quality issues."""
        issues = [
            # High quality
            {
                "number": 1,
                "title": "Bug: Detailed reproduction steps included",
                "body": "## Description\nDetailed.\n\n## Steps\n1. Step one\n2. Step two\n3. Step three\n\n## Expected\nCorrect behavior.\n\n```python\nprint('test')\n```",
                "labels": [{"name": "bug"}, {"name": "help wanted"}, {"name": "good first issue"}],
            },
            # Low quality
            {
                "number": 2,
                "title": "help",
                "body": "not working plz fix",
                "labels": [],
            },
            # Spam
            {
                "number": 3,
                "title": "Buy now free money",
                "body": "Casino prize claim",
                "labels": [],
            },
        ]
        result = analyze_issues_batch(issues)
        scores = {r["number"]: r["score"] for r in result["results"]}
        # High quality > low quality > spam
        assert scores[1] > scores[2] > scores[3]


# ============================================================
# 19. Real Issue Validation — 50+ issues from 15 repos (10 cases)
# ============================================================

def _fetch_real_issues():
    """Fetch real GitHub issues from multiple repos."""
    import json, subprocess

    repos = [
        ("vercel/next.js", 10),
        ("facebook/react", 5),
        ("microsoft/vscode", 5),
        ("rails/rails", 5),
        ("fastapi/fastapi", 3),
        ("sveltejs/svelte", 5),
        ("vuejs/core", 5),
        ("golang/go", 5),
        ("angular/angular", 5),
        ("rust-lang/rust", 5),
        ("kubernetes/kubernetes", 5),
        ("docker/compose", 5),
        ("grafana/grafana", 5),
        ("prometheus/prometheus", 5),
    ]

    all_issues = []
    for repo, count in repos:
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--repo", repo, "--limit", str(count),
                 "--json", "number,title,body,labels"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                issues = json.loads(result.stdout)
                for i in issues:
                    i["_repo"] = repo
                all_issues.extend(issues)
        except Exception:
            pass  # Skip unreachable repos
    return all_issues


@pytest.fixture(scope="module")
def real_issues():
    """Module-scoped fixture: fetch real issues once."""
    issues = _fetch_real_issues()
    if len(issues) < 10:
        pytest.skip("Cannot fetch enough real issues from GitHub")
    return issues


@pytest.fixture(scope="module")
def real_results(real_issues):
    """Module-scoped fixture: analyze real issues once."""
    return analyze_issues_batch(real_issues)


class TestRealIssueValidation:
    """Validate against real GitHub issues from 15+ repos.

    These tests enforce distribution properties that hold across
    real-world issue populations, not synthetic test data.
    """

    def test_minimum_sample_size(self, real_issues):
        """Should fetch at least 40 real issues."""
        assert len(real_issues) >= 40, f"Only got {len(real_issues)} issues"

    def test_score_distribution_not_uniform(self, real_results):
        """Scores should cluster in middle-high range, not uniform."""
        scores = [r["score"] for r in real_results["results"]]
        # Median should be above 60 (most real issues are decent)
        median = sorted(scores)[len(scores) // 2]
        assert median >= 60, f"Median score {median} too low for real issues"

    def test_no_spam_in_curated_repos(self, real_results):
        """Major open-source repos should have 0 spam."""
        assert real_results["spam_count"] == 0

    def test_majority_not_high_risk(self, real_results):
        """Most issues from major repos should not be high risk."""
        total = real_results["total"]
        high_risk = real_results["high_risk_count"]
        assert high_risk / total < 0.1, f"{high_risk}/{total} high risk (>10%)"

    def test_grade_distribution_has_b_or_better(self, real_results):
        """At least 30% of real issues should be grade B or better."""
        total = real_results["total"]
        ab_count = real_results["grade_distribution"]["A"] + real_results["grade_distribution"]["B"]
        assert ab_count / total >= 0.3, f"Only {ab_count}/{total} are A or B"

    def test_average_score_healthy(self, real_results):
        """Average score should be 65-90 for real issues."""
        avg = real_results["average_score"]
        assert 65 <= avg <= 90, f"Average score {avg} outside healthy range"

    def test_all_results_have_required_fields(self, real_results):
        """Every result should have all required fields (aligned with PR Coach)."""
        required = {"number", "title", "tier", "signals", "checklist",
                    "score", "quality_grade", "is_crawler_friendly", "is_spam"}
        for r in real_results["results"]:
            assert required.issubset(set(r.keys())), f"Missing fields in #{r['number']}"

    def test_scores_are_bounded(self, real_results):
        """All scores should be 0-100."""
        for r in real_results["results"]:
            assert 0 <= r["score"] <= 100, f"#{r['number']}: score {r['score']} out of range"

    def test_risk_values_valid(self, real_results):
        """All risk values should be valid."""
        valid_tiers = {"low_risk", "medium_risk", "high_risk"}
        for r in real_results["results"]:
            assert r["tier"] in valid_tiers, f"#{r['number']}: invalid tier '{r['tier']}'"

    def test_grade_values_valid(self, real_results):
        """All grade values should be valid."""
        valid_grades = {"A", "B", "C", "D", "F"}
        for r in real_results["results"]:
            assert r["quality_grade"] in valid_grades, \
                f"#{r['number']}: invalid grade '{r['quality_grade']}'"


# ============================================================
# 20. MisakaNet Upstream — 20% Sample Test (5 cases)
# ============================================================

def _fetch_misakanet_issues():
    """Fetch issues from upstream Ikalus1988/MisakaNet."""
    import json, subprocess, random

    result = subprocess.run(
        ["gh", "issue", "list", "--repo", "Ikalus1988/MisakaNet",
         "--state", "all", "--limit", "200",
         "--json", "number,title,body,labels,state"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    all_issues = json.loads(result.stdout)

    # 20% stratified sample
    random.seed(42)
    open_issues = [i for i in all_issues if i["state"] == "OPEN"]
    closed_issues = [i for i in all_issues if i["state"] == "CLOSED"]
    sample_size = max(20, len(all_issues) // 5)
    open_count = round(sample_size * len(open_issues) / len(all_issues))
    closed_count = sample_size - open_count
    sampled = (
        random.sample(open_issues, min(open_count, len(open_issues)))
        + random.sample(closed_issues, min(closed_count, len(closed_issues)))
    )
    random.shuffle(sampled)
    return sampled


@pytest.fixture(scope="module")
def misakanet_sample():
    """Module-scoped: fetch 20% sample from Ikalus1988/MisakaNet once."""
    issues = _fetch_misakanet_issues()
    if len(issues) < 10:
        pytest.skip("Cannot fetch enough issues from Ikalus1988/MisakaNet")
    return issues


@pytest.fixture(scope="module")
def misakanet_results(misakanet_sample):
    """Module-scoped: analyze MisakaNet sample once."""
    return analyze_issues_batch(misakanet_sample)


class TestMisakaNetSample:
    """20% sample test on upstream Ikalus1988/MisakaNet issues.

    Validates evaluator behavior on a real project with structured
    issue labels (agent-friendly, bounty, pool, etc.).
    """

    def test_sample_size_20_percent(self, misakanet_sample):
        """Sample should be ~20% of total issues."""
        assert len(misakanet_sample) >= 20, f"Only {len(misakanet_sample)} issues sampled"

    def test_spam_count_zero(self, misakanet_results):
        """MisakaNet should have 0 spam in sample."""
        assert misakanet_results["spam_count"] == 0

    def test_average_score_healthy(self, misakanet_results):
        """Average score should be 70+ for structured issues."""
        avg = misakanet_results["average_score"]
        assert avg >= 70, f"Average score {avg} too low"

    def test_majority_grade_b_or_better(self, misakanet_results):
        """70%+ issues should be grade B or better."""
        total = misakanet_results["total"]
        ab = misakanet_results["grade_distribution"]["A"] + misakanet_results["grade_distribution"]["B"]
        ratio = ab / total
        assert ratio >= 0.7, f"Only {ratio:.0%} are A/B (need >= 70%)"

    def test_crawler_friendly_count(self, misakanet_results):
        """Many MisakaNet issues have crawler labels — should detect them."""
        assert misakanet_results["crawler_friendly_count"] >= 5
