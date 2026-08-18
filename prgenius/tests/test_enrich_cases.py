"""Tests for scripts/enrich_cases.py"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestEnrichCases:
    """Test case enrichment pipeline."""

    def test_evidence_directory_exists(self):
        """Evidence directory should exist after pipeline run."""
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        assert evidence_dir.exists(), f"Evidence directory not found: {evidence_dir}"

    def test_evidence_files_are_valid_json(self):
        """All evidence files should be valid JSON."""
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        if not evidence_dir.exists():
            pytest.skip("Evidence directory not found")
        
        for evidence_file in evidence_dir.glob("*.json"):
            with open(evidence_file) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"Invalid JSON in {evidence_file}"

    def test_evidence_has_required_fields(self):
        """Evidence files should have required fields."""
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        if not evidence_dir.exists():
            pytest.skip("Evidence directory not found")
        
        required_fields = ["case_id", "pr_url", "outcome", "author", "verification"]
        
        for evidence_file in evidence_dir.glob("*.json"):
            with open(evidence_file) as f:
                data = json.load(f)
            
            for field in required_fields:
                assert field in data, f"Missing field '{field}' in {evidence_file}"

    def test_evidence_outcomes_are_valid(self):
        """Evidence outcomes should be merged, rejected, or open."""
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        if not evidence_dir.exists():
            pytest.skip("Evidence directory not found")
        
        valid_outcomes = {"merged", "rejected", "open"}
        
        for evidence_file in evidence_dir.glob("*.json"):
            with open(evidence_file) as f:
                data = json.load(f)
            
            outcome = data.get("outcome")
            assert outcome in valid_outcomes, f"Invalid outcome '{outcome}' in {evidence_file}"

    def test_evidence_verification_exists(self):
        """Evidence should have verification metadata."""
        evidence_dir = Path(__file__).parent.parent.parent / "evidence"
        if not evidence_dir.exists():
            pytest.skip("Evidence directory not found")
        
        for evidence_file in evidence_dir.glob("*.json"):
            with open(evidence_file) as f:
                data = json.load(f)
            
            verification = data.get("verification")
            assert verification is not None, f"Missing verification in {evidence_file}"
            assert "source" in verification, f"Missing verification.source in {evidence_file}"
            assert "timestamp" in verification, f"Missing verification.timestamp in {evidence_file}"
