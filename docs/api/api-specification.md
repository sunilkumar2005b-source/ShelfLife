# ShelfLife REST API Specification

## 1. API Architecture Overview

The ShelfLife backend is built using **FastAPI** (`0.141.1`) running on **Uvicorn** (`0.52.4`) on Python 3.13. It communicates directly with PostgreSQL (`shelflife_db`) using `psycopg2-binary` connection pooling and safe transaction context managers.

- **Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema (JSON):** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 2. Modular Endpoint Directory

| Tag | HTTP Method | Path | Summary / Action | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| **System** | `GET` | `/` | API availability check | `200 OK` |
| **System** | `GET` | `/health` | Health check verifying PostgreSQL connection | `200 OK` |
| **Products** | `GET` | `/products` | List all catalog perishable products | `200 OK` |
| **Products** | `GET` | `/products/{product_id}` | Retrieve single product details | `200 OK` / `404` |
| **Products** | `POST` | `/products` | Create a new perishable product | `201 Created` |
| **Products** | `PUT` | `/products/{product_id}` | Update existing product details | `200 OK` / `404` |
| **Products** | `DELETE`| `/products/{product_id}` | Delete product from catalog | `200 OK` / `400` / `404` |
| **Inventory**| `GET` | `/inventory` | List all inventory batches with expiry info | `200 OK` |
| **Inventory**| `GET` | `/inventory/{inventory_id}`| Retrieve single batch details | `200 OK` / `404` |
| **Inventory**| `POST` | `/inventory` | Add new batch to inventory | `201 Created` / `404` |
| **Inventory**| `PUT` | `/inventory/{inventory_id}`| Update batch quantity, expiry, or temp | `200 OK` / `404` |
| **Inventory**| `DELETE`| `/inventory/{inventory_id}`| Delete inventory batch | `200 OK` / `404` |
| **Sales** | `GET` | `/sales` | Retrieve historical sales transactions | `200 OK` |
| **Sales** | `POST` | `/sales` | Record new sale (with optional inventory deduction) | `201 Created` / `404` |
| **Suppliers**| `GET` | `/suppliers` | List all registered suppliers | `200 OK` |
| **Suppliers**| `POST` | `/suppliers` | Register a new supplier | `201 Created` |
| **Orders** | `GET` | `/purchase-orders` | List replenishment orders with total cost | `200 OK` |
| **Orders** | `POST` | `/purchase-orders` | Place a new purchase order | `201 Created` / `404` |
| **Weather** | `GET` | `/weather` | List environmental observations | `200 OK` |
| **Weather** | `POST` | `/weather` | Record weather observation | `201 Created` |
| **Analytics**| `GET` | `/demand-forecasts` | List forecasted sales volumes (Demo Seed Data)| `200 OK` |
| **Analytics**| `GET` | `/spoilage-predictions` | List spoilage probabilities (Demo Seed Data) | `200 OK` |
| **Analytics**| `GET` | `/dashboard-summary` | Aggregated KPI stats for executive dashboard | `200 OK` |
| **Analytics**| `GET` | `/inventory-intelligence`| Real-time inventory health & action recommendations| `200 OK` |
| **Analytics**| `GET` | `/inventory-intelligence-summary`| Count breakdown by recommendation type | `200 OK` |

---

## 3. Detailed Request / Response Contracts

### 3.1 Products API
#### `POST /products`
**Request Payload:**
```json
{
  "product_name": "Greek Yogurt",
  "category": "Dairy",
  "unit": "cup",
  "purchase_price": 30.00,
  "selling_price": 45.00,
  "shelf_life_days": 10
}
```
**Response (201 Created):**
```json
{
  "product_id": 9,
  "product_name": "Greek Yogurt",
  "category": "Dairy",
  "unit": "cup",
  "purchase_price": 30.0,
  "selling_price": 45.0,
  "shelf_life_days": 10
}
```

---

### 3.2 Inventory API
#### `POST /inventory`
**Request Payload:**
```json
{
  "product_id": 1,
  "batch_number": "MILK-B002",
  "quantity": 25,
  "purchase_date": "2026-09-18",
  "expiry_date": "2026-09-23",
  "storage_temperature": 3.8
}
```
**Response (201 Created):**
```json
{
  "inventory_id": 9,
  "product_id": 1,
  "product_name": "Milk",
  "category": "Dairy",
  "batch_number": "MILK-B002",
  "quantity": 25,
  "purchase_date": "2026-09-18",
  "expiry_date": "2026-09-23",
  "storage_temperature": 3.8
}
```

---

### 3.3 Inventory Intelligence API
#### `GET /inventory-intelligence`
Combines physical batches, catalog products, demand forecasts, and spoilage probabilities to compute health scores and actionable inventory recommendations.

**Sample Item Response (200 OK):**
```json
{
  "inventory_id": 1,
  "product_id": 1,
  "product_name": "Milk",
  "current_stock": 30,
  "predicted_demand": 12,
  "expiry_date": "2026-09-19",
  "days_remaining": 0,
  "spoilage_probability": 0.75,
  "spoilage_probability_percent": 75.0,
  "risk_level": "High",
  "health_score": 8,
  "health_status": "Critical",
  "recommendation": "Urgent Clearance",
  "ai_explanation": "30 units are currently in stock, while predicted demand is 12 units. Spoilage probability is 75%. The product expires in 0 day(s). Immediate clearance is recommended to reduce wastage."
}
```

---

## 4. Error Handling and Status Codes

- `200 OK`: Request succeeded, returns requested data.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Validation failure or business constraint violation (e.g. attempting to delete a product linked to foreign records).
- `404 Not Found`: Target entity ID does not exist in `shelflife_db`.
- `422 Unprocessable Entity`: Automatic FastAPI schema validation failure (e.g. string passed instead of integer, missing required fields).
- `500 Internal Server Error`: Database operational error or unhandled backend exception.
