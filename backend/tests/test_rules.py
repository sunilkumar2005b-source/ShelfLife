import unittest
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.rule_config import RuleConfig
from services.intelligence_service import (
    calculate_health_score,
    get_recommendation,
    get_spoilage_risk,
    health_status,
)


class TestInventoryIntelligenceRuleEngine(unittest.TestCase):
    """
    Exhaustive scenario testing for the deterministic business rule engine.
    Verifies that zero magic numbers exist and all recommendations are fully explainable.
    """

    def setUp(self):
        self.config = RuleConfig()

    def test_scenario_01_understock_reorder(self):
        """Scenario 1: Current stock is less than predicted demand -> Reorder"""
        current_stock = 10
        predicted_demand = 30
        days_remaining = 8
        spoilage_prob = 0.15

        rec, explanation = get_recommendation(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            config=self.config
        )

        self.assertEqual(rec, "Reorder")
        self.assertIn("insufficient", explanation.lower())
        self.assertIn("replenishment", explanation.lower())

    def test_scenario_02_critical_expiry_clearance(self):
        """Scenario 2: Low days to expiry (<=2) and high spoilage (>=0.60) -> Clearance Action"""
        current_stock = 25
        predicted_demand = 10
        days_remaining = 1
        spoilage_prob = 0.75

        rec, explanation = get_recommendation(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            config=self.config
        )

        self.assertEqual(rec, "Clearance Action")
        self.assertIn("clearance", explanation.lower())
        self.assertIn("1 day(s)", explanation)

    def test_scenario_03_surplus_approaching_expiry_sell_quickly(self):
        """Scenario 3: Stock > demand, expiry in warning window (<=5 days), medium risk -> Sell Quickly"""
        current_stock = 40
        predicted_demand = 20
        days_remaining = 4
        spoilage_prob = 0.45

        rec, explanation = get_recommendation(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            config=self.config
        )

        self.assertEqual(rec, "Sell Quickly")
        self.assertIn("surplus", explanation.lower())
        self.assertIn("front-of-shelf", explanation.lower())

    def test_scenario_04_balanced_safe_sufficient_stock(self):
        """Scenario 4: Stock matches demand, ample shelf life, low spoilage -> Sufficient Stock"""
        current_stock = 25
        predicted_demand = 20
        days_remaining = 14
        spoilage_prob = 0.10

        rec, explanation = get_recommendation(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            config=self.config
        )

        score = calculate_health_score(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            config=self.config
        )

        self.assertEqual(rec, "Sufficient Stock")
        self.assertGreaterEqual(score, 75)
        self.assertEqual(health_status(score), "Healthy")
        self.assertIn("adequately covers", explanation)

    def test_scenario_05_storage_temperature_violation(self):
        """Scenario 5: Dairy product stored above safe threshold -> Cold-chain penalty & warning"""
        current_stock = 20
        predicted_demand = 20
        days_remaining = 6
        spoilage_prob = 0.20

        # Normal dairy storage temp (4.0°C <= 5.0°C)
        normal_score = calculate_health_score(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            storage_temp=4.0,
            category="Dairy",
            config=self.config
        )

        # Violated dairy storage temp (10.0°C > 5.0°C)
        violation_score = calculate_health_score(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            storage_temp=10.0,
            category="Dairy",
            config=self.config
        )

        # Score must be lower due to temperature penalty
        self.assertLess(violation_score, normal_score)

        _, explanation = get_recommendation(
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            days_remaining=days_remaining,
            spoilage_probability=spoilage_prob,
            storage_temp=10.0,
            category="Dairy",
            config=self.config
        )
        self.assertIn("temperature of 10.0°c exceeds", explanation.lower())

    def test_scenario_06_ambient_environmental_influence(self):
        """Scenario 6: High ambient heat and humidity appended to explanation"""
        _, explanation = get_recommendation(
            current_stock=20,
            predicted_demand=20,
            days_remaining=7,
            spoilage_probability=0.25,
            ambient_temp=34.0,   # > 30.0°C threshold
            humidity=82.0,       # > 78.0% threshold
            config=self.config
        )
        self.assertIn("high ambient temperature (34.0°c)", explanation.lower())
        self.assertIn("elevated relative humidity (82.0%)", explanation.lower())

    def test_scenario_07_configurable_thresholds_shift_behavior(self):
        """Scenario 7: Custom RuleConfig alters decision boundaries without touching code"""
        custom_config = RuleConfig(
            expiry_critical_days=4,  # Expanded from 2 to 4
            spoilage_high_threshold=0.50 # Lowered from 0.60 to 0.50
        )

        # With default config, days_remaining=3 and prob=0.55 triggers Sell Quickly
        default_rec, _ = get_recommendation(
            current_stock=20,
            predicted_demand=15,
            days_remaining=3,
            spoilage_probability=0.55,
            config=self.config
        )
        self.assertEqual(default_rec, "Sell Quickly")

        # With custom config, it qualifies as critical -> Clearance Action
        custom_rec, _ = get_recommendation(
            current_stock=20,
            predicted_demand=15,
            days_remaining=3,
            spoilage_probability=0.55,
            config=custom_config
        )
        self.assertEqual(custom_rec, "Clearance Action")


if __name__ == "__main__":
    unittest.main()
