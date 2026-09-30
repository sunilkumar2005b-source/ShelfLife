# ShelfLife - Project Overview & Baseline Inspection

## Project Title
**ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System for Small Retail Stores**

## Academic Classification
Final-Year Integrated M.Tech Software Engineering Project

---

## 1. Inspection Findings

A comprehensive baseline inspection of the repository was completed on Windows 11.

### 1.1 Existing Directory Structure
- `backend/`: FastAPI backend service with `database.py`, `main.py`, and a Python 3.13 virtual environment (`venv/`).
- `frontend/`: React 19 + Vite 8 single-page application with complete dependencies installed in `node_modules/`.
- `ml/`: Initialized directory; currently empty (no datasets or pickled models present).

### 1.2 Identified APIs in `backend/main.py`
All 13 existing backend routes are functional GET endpoints:
1. `GET /` — API root status.
2. `GET /health` — Service and PostgreSQL connectivity health check.
3. `GET /products` — Product catalog listing.
4. `GET /inventory` — Product batches with expiry dates, quantities, and storage temperatures.
5. `GET /sales` — Transaction history with prices and timestamps.
6. `GET /suppliers` — Supplier contact and lead time information.
7. `GET /purchase-orders` — Restock orders with calculated totals and status.
8. `GET /weather` — Historical weather records (temperature, humidity, rainfall).
9. `GET /demand-forecasts` — Forecast records (currently synthetic/demo records).
10. `GET /spoilage-predictions` — Spoilage risk probabilities (currently synthetic/demo records).
11. `GET /dashboard-summary` — High-level metrics for dashboard cards.
12. `GET /inventory-intelligence` — Real-time combination of inventory, expiry days, risk, and rule-based recommendation.
13. `GET /inventory-intelligence-summary` — Aggregated counts by recommendation category.

### 1.3 Database (`shelflife_db`) Status
- **Engine**: PostgreSQL 18.x running as a Windows service on port 5432.
- **Connection**: Operational via `psycopg2-binary`.
- **Existing Tables**:
  - `products` (8 rows)
  - `inventory` (8 rows)
  - `sales` (10 rows)
  - `suppliers` (4 rows)
  - `purchase_orders` (7 rows)
  - `weather_data` (5 rows)
  - `demand_forecasts` (8 rows)
  - `spoilage_predictions` (8 rows)
  - `analytics` (8 rows)
  - `users` (0 rows)

### 1.4 Frontend Pages & Views
The frontend in `frontend/src/App.jsx` implements the following interactive tabs:
1. **Dashboard**: KPI stat cards, inventory health breakdown, and risk distribution.
2. **Products**: Table of products, categories, shelf life, and pricing.
3. **Inventory**: Detailed view of batch numbers, remaining days to expiry, and temperatures.
4. **Spoilage Risk**: Risk level classification and probabilities.
5. **Demand Forecast**: Historical demand comparison against forecasted sales.
6. **Inventory Intelligence**: Comprehensive health scoring, actionable recommendation tags, and generated natural language explanations.

---

## 2. Working vs. Non-Working / Incomplete Features

### Working Features
- PostgreSQL connectivity and active schema with sample demo records.
- FastAPI backend server running on `http://127.0.0.1:8000`.
- Swagger documentation accessible at `http://127.0.0.1:8000/docs`.
- React + Vite development server running on `http://localhost:5173`.
- End-to-end data fetching between React frontend and FastAPI backend.
- Heuristic recommendation engine calculating health scores and clearance/reorder rules.

### Broken / Incomplete / Technical Debt Identified
1. **No Mutations / CRUD**: Backend currently only supports `GET` requests; adding/editing/deleting products, batches, sales, and purchase orders is not yet implemented (scheduled for Section 3).
2. **Hardcoded Database Credentials**: `backend/database.py` contains plaintext credentials rather than reading from `.env`.
3. **No Trained ML Models**: `demand_forecasts` and `spoilage_predictions` records in the database carry `model_name = 'Random Forest'`, but `ml/` is empty and no trained models exist. These records are synthetic demo data.
4. **Monolithic Frontend**: `App.jsx` is 1,476 lines containing all navigation, styles, business rules, and views in one file. Business rule formulas are duplicated between backend and frontend.
5. **No Structured Test Suite**: Automated tests for backend endpoints and schema validation have not yet been established.
