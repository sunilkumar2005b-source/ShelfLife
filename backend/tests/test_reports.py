"""
Test Suite for Section 9: Advanced Analytics, Financial Valuation, Reports, and Demo Scenarios
"""

import json
import unittest
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def request_raw(method: str, path: str, data: dict = None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            content = resp.read().decode("utf-8")
            if "application/json" in content_type:
                return resp.status, json.loads(content)
            return resp.status, content
    except urllib.error.HTTPError as err:
        content = err.read().decode("utf-8")
        return err.code, json.loads(content) if "application/json" in err.headers.get("Content-Type", "") else content


class TestAdvancedAnalyticsAndReports(unittest.TestCase):
    def test_01_financial_risk_summary(self):
        """Verify GET /reports/financial-risk returns store-level valuation and risk exposure."""
        status_code, data = request_raw("GET", "/reports/financial-risk")
        self.assertEqual(status_code, 200)
        self.assertIn("total_inventory_cost_valuation", data)
        self.assertIn("capital_at_high_risk", data)
        self.assertIn("projected_lost_retail_margin", data)
        self.assertIn("category_risk_breakdown", data)
        self.assertGreaterEqual(data["total_inventory_cost_valuation"], 0.0)

    def test_02_simulate_clearance_markdown(self):
        """Verify POST /reports/simulate-clearance calculates capital salvaging correctly."""
        payload = {"discount_percent": 25.0}
        status_code, data = request_raw("POST", "/reports/simulate-clearance", payload)
        self.assertEqual(status_code, 200)
        self.assertIn("estimated_discounted_revenue_recovered", data)
        self.assertIn("unmitigated_cost_loss", data)
        self.assertEqual(data["discount_percentage_applied"], 25.0)

    def test_03_inventory_audit_csv_export(self):
        """Verify GET /reports/inventory-audit.csv streams formatted CSV."""
        status_code, text = request_raw("GET", "/reports/inventory-audit.csv")
        self.assertEqual(status_code, 200)
        lines = text.strip().split("\n")
        self.assertGreater(len(lines), 1)
        header = lines[0]
        self.assertIn("Batch ID", header)
        self.assertIn("Cost Price", header)
        self.assertIn("Spoilage Probability", header)

    def test_04_spoilage_risk_csv_export(self):
        """Verify GET /reports/spoilage-risk.csv streams formatted CSV."""
        status_code, text = request_raw("GET", "/reports/spoilage-risk.csv")
        self.assertEqual(status_code, 200)
        lines = text.strip().split("\n")
        self.assertGreater(len(lines), 1)
        header = lines[0]
        self.assertIn("Prediction ID", header)
        self.assertIn("Capital At Risk", header)

    def test_05_demo_scenarios_switching(self):
        """Verify POST /demo/apply-scenario handles preset crisis transitions and resets cleanly."""
        # 1. Apply Heatwave
        status_code, res = request_raw("POST", "/demo/apply-scenario", {"scenario": "heatwave"})
        self.assertEqual(status_code, 200)
        self.assertTrue(res["success"])
        self.assertEqual(res["scenario_applied"], "heatwave")

        # 2. Apply Urgent Clearance
        status_code, res = request_raw("POST", "/demo/apply-scenario", {"scenario": "urgent_clearance"})
        self.assertEqual(status_code, 200)
        self.assertEqual(res["scenario_applied"], "urgent_clearance")

        # 3. Apply Stockout Crisis
        status_code, res = request_raw("POST", "/demo/apply-scenario", {"scenario": "stockout_crisis"})
        self.assertEqual(status_code, 200)
        self.assertEqual(res["scenario_applied"], "stockout_crisis")

        # 4. Reset to Normal
        status_code, res = request_raw("POST", "/demo/apply-scenario", {"scenario": "normal"})
        self.assertEqual(status_code, 200)
        self.assertEqual(res["scenario_applied"], "normal")


if __name__ == "__main__":
    unittest.main()
