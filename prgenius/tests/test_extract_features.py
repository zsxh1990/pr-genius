"""Tests for scripts/extract_features.py"""

import json
import pytest
from pathlib import Path


class TestExtractFeatures:
    """Test feature extraction pipeline."""

    def test_features_file_exists(self):
        """Features file should exist after pipeline run."""
        features_file = Path(__file__).parent.parent.parent / "features" / "features.json"
        assert features_file.exists(), f"Features file not found: {features_file}"

    def test_features_are_valid_json(self):
        """Features file should be valid JSON."""
        features_file = Path(__file__).parent.parent.parent / "features" / "features.json"
        if not features_file.exists():
            pytest.skip("Features file not found")
        
        with open(features_file) as f:
            data = json.load(f)
        assert isinstance(data, list), "Features should be a list"

    def test_features_have_required_fields(self):
        """Feature vectors should have required fields."""
        features_file = Path(__file__).parent.parent.parent / "features" / "features.json"
        if not features_file.exists():
            pytest.skip("Features file not found")
        
        with open(features_file) as f:
            data = json.load(f)
        
        required_fields = ["case_id", "outcome", "human_reviews", "author_association"]
        
        for features in data:
            for field in required_fields:
                assert field in features, f"Missing field '{field}' in features"

    def test_features_outcomes_match_evidence(self):
        """Feature outcomes should match evidence outcomes."""
        features_file = Path(__file__).parent.parent.parent / "features" / "features.json"
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        
        if not features_file.exists() or not evidence_dir.exists():
            pytest.skip("Features or evidence not found")
        
        with open(features_file) as f:
            features_data = json.load(f)
        
        evidence_outcomes = {}
        for evidence_file in evidence_dir.glob("*.json"):
            with open(evidence_file) as f:
                evidence = json.load(f)
            evidence_outcomes[evidence["case_id"]] = evidence["outcome"]
        
        for features in features_data:
            case_id = features["case_id"]
            if case_id in evidence_outcomes:
                assert features["outcome"] == evidence_outcomes[case_id], \
                    f"Outcome mismatch for {case_id}: {features['outcome']} vs {evidence_outcomes[case_id]}"

    def test_features_numerical_values_are_valid(self):
        """Numerical feature values should be valid."""
        features_file = Path(__file__).parent.parent.parent / "features" / "features.json"
        if not features_file.exists():
            pytest.skip("Features file not found")
        
        with open(features_file) as f:
            data = json.load(f)
        
        for features in data:
            # Check non-negative counts
            assert features.get("human_reviews", 0) >= 0, f"Negative human_reviews in {features['case_id']}"
            assert features.get("bot_reviews", 0) >= 0, f"Negative bot_reviews in {features['case_id']}"
            assert features.get("additions", 0) >= 0, f"Negative additions in {features['case_id']}"
            assert features.get("deletions", 0) >= 0, f"Negative deletions in {features['case_id']}"
