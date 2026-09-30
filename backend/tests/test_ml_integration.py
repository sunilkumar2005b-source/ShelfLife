"""
Integration Test Suite for Section 8: ML Endpoints & Batch Synchronization
Verifies FastAPI ML routes, database prediction persistence, and end-to-end intelligence synthesis.
Uses standard library urllib.request to interact with the live backend server.
"""

import json
import unittest
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def request_json(method: str, path: str, data: dict = None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as err:
        content = err.read().decode("utf-8")
        return err.code, json.loads(content) if content else {}


class TestMLIntegration(unittest.TestCase):
    def test_01_ml_status_endpoint(self):
        """Verify GET /ml/status returns operational models and metrics."""
        status_code, data = request_json("GET", "/ml/status")
        self.assertEqual(status_code, 200)
        self.assertIn("status", data)
        self.assertIn("demand_model", data)
        self.assertIn("spoilage_model", data)
        self.assertEqual(data["demand_model"]["champion_model"], "Ridge Regression (alpha=1.0)")
        self.assertEqual(data["spoilage_model"]["champion_model"], "Logistic Regression")

    def test_02_predict_demand_live_endpoint(self):
        """Verify POST /ml/predict/demand returns realistic continuous demand units."""
        payload = {
            "product_id": 1,
            "category": "Dairy",
            "stock_quantity": 25,
            "reorder_level": 15,
            "reorder_quantity": 20,
            "unit_price": 4.5,
            "shelf_life_days": 10,
        }
        status_code, data = request_json("POST", "/ml/predict/demand", payload)
        self.assertEqual(status_code, 200)
        self.assertIn("predicted_demand", data)
        self.assertGreater(data["predicted_demand"], 0.0)
        self.assertEqual(data["model_name"], "Ridge Regression (Trained ML)")

    def test_03_predict_spoilage_live_endpoint(self):
        """Verify POST /ml/predict/spoilage returns calibrated risk tier and probability."""
        payload = {
            "category": "Fruits & Vegetables",
            "stock_quantity": 50,
            "days_remaining": 2,
            "unit_price": 3.0,
            "sales_volume": 40.0,
            "turnover_rate": 35.0,
            "total_shelf_life": 12,
        }
        status_code, data = request_json("POST", "/ml/predict/spoilage", payload)
        self.assertEqual(status_code, 200)
        self.assertIn("risk_level", data)
        self.assertIn("spoilage_probability", data)
        self.assertIn(data["risk_level"], ["Low", "Medium", "High"])
        self.assertEqual(data["model_name"], "Logistic Regression (Trained ML)")

    def test_04_sync_predictions_into_database(self):
        """Verify POST /ml/sync-predictions persists predictions to demand_forecasts and spoilage_predictions."""
        status_code, data = request_json("POST", "/ml/sync-predictions")
        self.assertEqual(status_code, 200)
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["synced_demand_forecasts"], 1)
        self.assertGreaterEqual(data["synced_spoilage_predictions"], 1)

    def test_05_demand_forecasts_contain_trained_ml_attribution(self):
        """Verify GET /demand-forecasts serves records labeled with trained ML model."""
        status_code, forecasts = request_json("GET", "/demand-forecasts")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(forecasts), 0)
        for f in forecasts:
            self.assertIn("Ridge Regression (Trained ML)", f["model_name"])
            self.assertGreaterEqual(f["predicted_demand"], 0.0)

    def test_06_spoilage_predictions_contain_trained_ml_attribution(self):
        """Verify GET /spoilage-predictions serves records labeled with trained ML classifier."""
        status_code, predictions = request_json("GET", "/spoilage-predictions")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(predictions), 0)
        for p in predictions:
            self.assertIn("Logistic Regression (Trained ML)", p["model_name"])
            self.assertGreaterEqual(p["spoilage_probability"], 0.0)
            self.assertLessEqual(p["spoilage_probability"], 1.0)

    def test_07_inventory_intelligence_synthesizes_ml_predictions(self):
        """Verify GET /inventory-intelligence fuses live ML predictions into health scores."""
        status_code, items = request_json("GET", "/inventory-intelligence")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(items), 0)
        for item in items:
            self.assertIn("health_score", item)
            self.assertIn("recommendation", item)
            self.assertIn("ai_explanation", item)
            self.assertGreaterEqual(item["health_score"], 0)
            self.assertLessEqual(item["health_score"], 100)


if __name__ == "__main__":
    unittest.main()
