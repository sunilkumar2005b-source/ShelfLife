# Machine Learning API Specification & Integration Guide

## 1. Overview
Section 8 integrates the trained scikit-learn models (Ridge Regression for Demand Forecasting, Logistic Regression for Spoilage Risk Classification) into the FastAPI backend, PostgreSQL database (`shelflife_db`), and React Vite frontend.

All synthetic demo data seeds have been replaced with live ML predictions with explicit model provenance tracking.

---

## 2. API Endpoints

### 2.1 `GET /ml/status`
Returns runtime model health, champion model identifiers, test set evaluation metrics, and artifact locations.

- **Method**: `GET`
- **Authentication**: None (Public)
- **Response**: `200 OK`
```json
{
  "status": "Models Loaded and Operational",
  "demand_model": {
    "task": "Perishable Demand Forecasting (Sales Volume Regression)",
    "champion_model": "Ridge Regression (alpha=1.0)",
    "metrics": {
      "MAE": 19.4481,
      "RMSE": 22.7541,
      "R2_Score": -0.0308,
      "MAPE_Percent": 43.5
    },
    "training_samples": 791,
    "testing_samples": 198,
    "artifact_path": "ml/models/demand_forecast_model.joblib"
  },
  "spoilage_model": {
    "task": "Perishable Spoilage Risk Tier & Probability Classification",
    "champion_model": "Logistic Regression",
    "metrics": {
      "Accuracy": 0.8889,
      "Precision_Weighted": 0.8746,
      "Recall_Weighted": 0.8889,
      "F1_Score_Weighted": 0.8787
    },
    "training_samples": 791,
    "testing_samples": 198,
    "artifact_path": "ml/models/spoilage_risk_model.joblib"
  }
}
```

---

### 2.2 `POST /ml/predict/demand`
Executes on-demand inference using the champion Ridge Regression model. Accepts either an existing `product_id` (auto-fetching inventory stock and pricing) or arbitrary hypothetical attributes.

- **Method**: `POST`
- **Request Body**:
```json
{
  "product_id": 1,
  "category": "Dairy",
  "stock_quantity": 25,
  "reorder_level": 15,
  "reorder_quantity": 20,
  "unit_price": 4.5,
  "shelf_life_days": 10
}
```
- **Response**: `200 OK`
```json
{
  "product_id": 1,
  "product_name": "Milk",
  "category": "Dairy",
  "predicted_demand": 55.42,
  "model_name": "Ridge Regression (Trained ML)",
  "input_features": {
    "category": "Dairy",
    "stock_quantity": 25,
    "reorder_level": 30,
    "reorder_quantity": 20,
    "unit_price": 55.0,
    "shelf_life_days": 5,
    "month": 9,
    "day_of_week": 2
  }
}
```

---

### 2.3 `POST /ml/predict/spoilage`
Executes real-time classification and calibrated probability estimation for an inventory batch using the champion Logistic Regression classifier.

- **Method**: `POST`
- **Request Body**:
```json
{
  "inventory_id": 1,
  "category": "Dairy",
  "stock_quantity": 25,
  "days_remaining": 2,
  "unit_price": 4.5
}
```
- **Response**: `200 OK`
```json
{
  "inventory_id": 1,
  "product_id": 1,
  "product_name": "Milk",
  "risk_level": "High",
  "spoilage_probability": 0.9926,
  "class_probabilities": {
    "High": 0.9926,
    "Low": 0.0001,
    "Medium": 0.0072
  },
  "model_name": "Logistic Regression (Trained ML)"
}
```

---

### 2.4 `POST /ml/sync-predictions`
Triggers an automated batch synchronization routine across all products and active inventory in `shelflife_db`:
1. Clears prior predictions to guarantee idempotency.
2. Iterates over all products in `products`, executes `predict_demand()`, and inserts into `demand_forecasts`.
3. Iterates over all batches in `inventory`, executes `predict_spoilage()`, and inserts into `spoilage_predictions`.
4. Updates timestamps and sets `model_name` attribution.

- **Method**: `POST`
- **Response**: `200 OK`
```json
{
  "success": true,
  "synced_demand_forecasts": 8,
  "synced_spoilage_predictions": 8,
  "message": "Successfully generated 8 demand forecasts and 8 spoilage predictions using trained ML models."
}
```

---

### 2.5 Updated Core Endpoints

| Endpoint | Method | Previous State (Section 3-5) | New State (Section 8) |
| :--- | :--- | :--- | :--- |
| `GET /demand-forecasts` | `GET` | Served static `'Random Forest (Demo Seed)'` records | Serves genuine `'Ridge Regression (Trained ML)'` predictions |
| `GET /spoilage-predictions` | `GET` | Served static `'Random Forest (Demo Seed)'` records | Serves genuine `'Logistic Regression (Trained ML)'` probabilities |
| `GET /inventory-intelligence` | `GET` | Joined with static demo records | Synthesizes genuine ML forecasts & spoilage probabilities with rule engine |
| `GET /dashboard-summary` | `GET` | Aggregated demo counts | Aggregates live trained ML risk distribution |

---

## 3. Database Persistence & Integrity

Predictions are persisted directly into PostgreSQL:
- `demand_forecasts`:
  - `forecast_id` (PK)
  - `product_id` (FK &rarr; `products`)
  - `forecast_date` (DATE)
  - `predicted_demand` (NUMERIC, $\ge 0$)
  - `model_name` (`'Ridge Regression (Trained ML)'`)
- `spoilage_predictions`:
  - `prediction_id` (PK)
  - `product_id` (FK &rarr; `products`)
  - `inventory_id` (FK &rarr; `inventory`)
  - `prediction_date` (DATE)
  - `days_remaining` (INT, $\ge 0$)
  - `spoilage_probability` (NUMERIC, $0.0 \le P \le 1.0$)
  - `risk_level` (`'Low'`, `'Medium'`, `'High'`)
  - `model_name` (`'Logistic Regression (Trained ML)'`)

---

## 4. Verification

To verify all ML integration endpoints and database synchronizations:
```powershell
& "backend\venv\Scripts\python.exe" -m unittest backend\tests\test_ml_integration.py
```
All 7 integration tests pass with 100% OK.
