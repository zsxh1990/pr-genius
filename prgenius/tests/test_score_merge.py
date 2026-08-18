"""Tests for scripts/score_merge.py"""

import json
import pytest
from pathlib import Path


class TestScoreMerge:
    """Test merge scoring pipeline."""

    def test_predictions_file_exists(self):
        """Predictions file should exist after pipeline run."""
        predictions_file = Path(__file__).parent.parent.parent / "predictions" / "predictions.json"
        assert predictions_file.exists(), f"Predictions file not found: {predictions_file}"

    def test_predictions_are_valid_json(self):
        """Predictions file should be valid JSON."""
        predictions_file = Path(__file__).parent.parent.parent / "predictions" / "predictions.json"
        if not predictions_file.exists():
            pytest.skip("Predictions file not found")
        
        with open(predictions_file) as f:
            data = json.load(f)
        assert isinstance(data, list), "Predictions should be a list"

    def test_predictions_have_required_fields(self):
        """Prediction entries should have required fields."""
        predictions_file = Path(__file__).parent.parent.parent / "predictions" / "predictions.json"
        if not predictions_file.exists():
            pytest.skip("Predictions file not found")
        
        with open(predictions_file) as f:
            data = json.load(f)
        
        required_fields = ["case_id", "actual_outcome", "prediction", "merge_probability"]
        
        for pred in data:
            for field in required_fields:
                assert field in pred, f"Missing field '{field}' in prediction"

    def test_predictions_probabilities_are_valid(self):
        """Merge probabilities should be between 0 and 1."""
        predictions_file = Path(__file__).parent.parent.parent / "predictions" / "predictions.json"
        if not predictions_file.exists():
            pytest.skip("Predictions file not found")
        
        with open(predictions_file) as f:
            data = json.load(f)
        
        for pred in data:
            prob = pred.get("merge_probability", 0)
            assert 0 <= prob <= 1, f"Invalid probability {prob} in {pred['case_id']}"

    def test_predictions_outcomes_are_valid(self):
        """Prediction outcomes should be valid."""
        predictions_file = Path(__file__).parent.parent.parent / "predictions" / "predictions.json"
        if not predictions_file.exists():
            pytest.skip("Predictions file not found")
        
        with open(predictions_file) as f:
            data = json.load(f)
        
        valid_outcomes = {"merged", "rejected", "open"}
        valid_predictions = {"merge", "likely_merge", "unlikely_merge"}
        
        for pred in data:
            assert pred.get("actual_outcome") in valid_outcomes, \
                f"Invalid actual_outcome '{pred.get('actual_outcome')}' in {pred['case_id']}"
            assert pred.get("prediction") in valid_predictions, \
                f"Invalid prediction '{pred.get('prediction')}' in {pred['case_id']}"

    def test_evaluation_file_exists(self):
        """Evaluation file should exist after pipeline run."""
        evaluation_file = Path(__file__).parent.parent.parent / "predictions" / "evaluation.json"
        assert evaluation_file.exists(), f"Evaluation file not found: {evaluation_file}"

    def test_evaluation_accuracy_is_valid(self):
        """Evaluation accuracy should be between 0 and 1."""
        evaluation_file = Path(__file__).parent.parent.parent / "predictions" / "evaluation.json"
        if not evaluation_file.exists():
            pytest.skip("Evaluation file not found")
        
        with open(evaluation_file) as f:
            data = json.load(f)
        
        accuracy = data.get("accuracy", 0)
        assert 0 <= accuracy <= 1, f"Invalid accuracy {accuracy}"

    def test_evaluation_metrics_are_consistent(self):
        """Evaluation metrics should be internally consistent."""
        evaluation_file = Path(__file__).parent.parent.parent / "predictions" / "evaluation.json"
        if not evaluation_file.exists():
            pytest.skip("Evaluation file not found")
        
        with open(evaluation_file) as f:
            data = json.load(f)
        
        tp = data.get("true_positives", 0)
        fp = data.get("false_positives", 0)
        tn = data.get("true_negatives", 0)
        fn = data.get("false_negatives", 0)
        
        total = tp + fp + tn + fn
        correct = tp + tn
        
        assert total == data.get("total", 0), "Total mismatch"
        assert correct == data.get("correct", 0), "Correct count mismatch"
        
        if total > 0:
            assert abs(data.get("accuracy", 0) - correct / total) < 0.01, "Accuracy mismatch"
