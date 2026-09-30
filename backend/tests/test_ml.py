"""
Automated Test Suite for ShelfLife Machine Learning Models & Inference Pipeline
Verifies model loading, numerical boundaries, categorization, and edge-case handling.
"""

import unittest
from pathlib import Path
import sys

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.inference import predict_demand, predict_spoilage, load_demand_pipeline, load_spoilage_pipeline


class TestMachineLearningModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load pipelines to verify artifact existence
        cls.demand_model, cls.demand_preprocessor = load_demand_pipeline()
        cls.spoilage_bundle = load_spoilage_pipeline()

    def test_01_artifacts_exist_and_loaded(self):
        """Verify model artifacts are loaded in memory."""
        self.assertIsNotNone(self.demand_model)
        self.assertIsNotNone(self.demand_preprocessor)
        self.assertIn("model", self.spoilage_bundle)
        self.assertIn("preprocessor", self.spoilage_bundle)
        self.assertIn("classes", self.spoilage_bundle)

    def test_02_predict_demand_valid_output(self):
        """Verify demand prediction returns expected format and non-negative output."""
        result = predict_demand(
            category="Fruits & Vegetables",
            stock_quantity=50,
            reorder_level=30,
            reorder_quantity=20,
            unit_price=4.0,
            shelf_life_days=12,
            month=5,
            day_of_week=2,
        )
        self.assertIn("predicted_demand", result)
        self.assertIn("model_name", result)
        self.assertGreaterEqual(result["predicted_demand"], 0.0)
        self.assertEqual(result["model_name"], "Ridge Regression (Trained ML)")

    def test_03_predict_demand_unknown_category_robustness(self):
        """Verify pipeline handles unknown product categories gracefully without failing."""
        result = predict_demand(
            category="Exotic Specialty Produce",
            stock_quantity=10,
            reorder_level=5,
            reorder_quantity=10,
            unit_price=12.50,
            shelf_life_days=7,
        )
        self.assertGreaterEqual(result["predicted_demand"], 0.0)

    def test_04_predict_spoilage_high_risk_scenario(self):
        """Verify high stock with 1 day remaining is flagged as High Spoilage Risk."""
        result = predict_spoilage(
            category="Dairy",
            stock_quantity=90,
            days_remaining=1,
            reorder_level=20,
            reorder_quantity=15,
            unit_price=3.50,
            sales_volume=20,
            turnover_rate=15,
            total_shelf_life=10,
        )
        self.assertEqual(result["risk_level"], "High")
        self.assertGreaterEqual(result["spoilage_probability"], 0.60)
        self.assertLessEqual(result["spoilage_probability"], 1.0)

    def test_05_predict_spoilage_low_risk_scenario(self):
        """Verify healthy stock with long remaining shelf life is flagged as Low Risk."""
        result = predict_spoilage(
            category="Grains & Pulses",
            stock_quantity=15,
            days_remaining=120,
            reorder_level=25,
            reorder_quantity=50,
            unit_price=2.00,
            sales_volume=80,
            turnover_rate=90,
            total_shelf_life=180,
        )
        self.assertEqual(result["risk_level"], "Low")
        self.assertLessEqual(result["spoilage_probability"], 0.40)

    def test_06_spoilage_class_probabilities_sum_to_one(self):
        """Verify predicted class probabilities sum to approximately 1.0."""
        result = predict_spoilage(
            category="Bakery",
            stock_quantity=30,
            days_remaining=3,
        )
        prob_dict = result["class_probabilities"]
        prob_sum = sum(prob_dict.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
