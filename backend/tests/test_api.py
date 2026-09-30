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


class TestShelfLifeBackendAPI(unittest.TestCase):

    def test_01_root_and_health(self):
        """Test GET / and GET /health"""
        status_code, body = request_json("GET", "/")
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("status"), "online")

        status_code, body = request_json("GET", "/health")
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("status"), "healthy")
        self.assertEqual(body.get("database"), "connected")

    def test_02_products_crud(self):
        """Test GET /products, POST, GET/{id}, PUT, DELETE"""
        # GET all
        status_code, body = request_json("GET", "/products")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)
        self.assertGreater(len(body), 0)

        # GET single existing
        status_code, body = request_json("GET", "/products/1")
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("product_id"), 1)

        # POST new product
        new_prod = {
            "product_name": "API Test Butter",
            "category": "Dairy",
            "unit": "packet",
            "purchase_price": 50.0,
            "selling_price": 65.0,
            "shelf_life_days": 14
        }
        status_code, created = request_json("POST", "/products", new_prod)
        self.assertEqual(status_code, 201)
        prod_id = created.get("product_id")
        self.assertIsNotNone(prod_id)

        # PUT update
        status_code, updated = request_json("PUT", f"/products/{prod_id}", {"selling_price": 70.0})
        self.assertEqual(status_code, 200)
        self.assertEqual(updated.get("selling_price"), 70.0)

        # DELETE
        status_code, deleted = request_json("DELETE", f"/products/{prod_id}")
        self.assertEqual(status_code, 200)

        # Confirm 404
        status_code, _ = request_json("GET", f"/products/{prod_id}")
        self.assertEqual(status_code, 404)

    def test_03_inventory_crud(self):
        """Test GET /inventory, POST, GET/{id}, PUT, DELETE"""
        status_code, body = request_json("GET", "/inventory")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)

        # GET existing
        status_code, body = request_json("GET", "/inventory/1")
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("inventory_id"), 1)

        # POST new inventory batch
        new_batch = {
            "product_id": 1,
            "batch_number": "TEST-B100",
            "quantity": 10,
            "purchase_date": "2026-09-01",
            "expiry_date": "2026-09-25",
            "storage_temperature": 4.0
        }
        status_code, created = request_json("POST", "/inventory", new_batch)
        self.assertEqual(status_code, 201)
        inv_id = created.get("inventory_id")

        # PUT update
        status_code, updated = request_json("PUT", f"/inventory/{inv_id}", {"quantity": 15})
        self.assertEqual(status_code, 200)
        self.assertEqual(updated.get("quantity"), 15)

        # DELETE
        status_code, _ = request_json("DELETE", f"/inventory/{inv_id}")
        self.assertEqual(status_code, 200)

    def test_04_sales(self):
        """Test GET /sales and POST /sales"""
        status_code, body = request_json("GET", "/sales")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)

        new_sale = {
            "product_id": 1,
            "quantity_sold": 1,
            "selling_price": 55.0
        }
        status_code, created = request_json("POST", "/sales", new_sale)
        self.assertEqual(status_code, 201)
        self.assertEqual(created.get("product_id"), 1)

    def test_05_suppliers(self):
        """Test GET /suppliers and POST /suppliers"""
        status_code, body = request_json("GET", "/suppliers")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)

        new_sup = {
            "supplier_name": "API Test Organic Dairy",
            "contact_person": "Praveen",
            "phone": "9812345678",
            "email": "praveen@testorganic.com",
            "average_delivery_days": 2,
            "minimum_order_quantity": 5
        }
        status_code, created = request_json("POST", "/suppliers", new_sup)
        self.assertEqual(status_code, 201)
        self.assertEqual(created.get("supplier_name"), "API Test Organic Dairy")

    def test_06_purchase_orders(self):
        """Test GET /purchase-orders and POST /purchase-orders"""
        status_code, body = request_json("GET", "/purchase-orders")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)

        new_po = {
            "supplier_id": 1,
            "product_id": 1,
            "quantity_ordered": 10,
            "unit_cost": 45.0
        }
        status_code, created = request_json("POST", "/purchase-orders", new_po)
        self.assertEqual(status_code, 201)
        self.assertEqual(created.get("quantity_ordered"), 10)
        self.assertEqual(created.get("total_cost"), 450.0)

    def test_07_weather(self):
        """Test GET /weather and POST /weather"""
        status_code, body = request_json("GET", "/weather")
        self.assertEqual(status_code, 200)
        self.assertIsInstance(body, list)

        new_weather = {
            "location": "Chennai-West",
            "temperature": 33.5,
            "humidity": 70.0,
            "rainfall": 0.0
        }
        status_code, created = request_json("POST", "/weather", new_weather)
        self.assertEqual(status_code, 201)
        self.assertEqual(created.get("location"), "Chennai-West")

    def test_08_analytics_and_intelligence(self):
        """Test demand-forecasts, spoilage-predictions, dashboard-summary, intelligence"""
        # Forecasts
        status_code, forecasts = request_json("GET", "/demand-forecasts")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(forecasts), 0)

        # Spoilage
        status_code, spoilage = request_json("GET", "/spoilage-predictions")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(spoilage), 0)

        # Dashboard summary
        status_code, dash = request_json("GET", "/dashboard-summary")
        self.assertEqual(status_code, 200)
        self.assertIn("total_products", dash)
        self.assertIn("risk_summary", dash)

        # Intelligence
        status_code, intel = request_json("GET", "/inventory-intelligence")
        self.assertEqual(status_code, 200)
        self.assertGreater(len(intel), 0)
        first_item = intel[0]
        self.assertIn("health_score", first_item)
        self.assertIn("recommendation", first_item)
        self.assertIn("ai_explanation", first_item)

        # Intelligence summary
        status_code, isum = request_json("GET", "/inventory-intelligence-summary")
        self.assertEqual(status_code, 200)
        self.assertIn("total", isum)


if __name__ == "__main__":
    unittest.main()
