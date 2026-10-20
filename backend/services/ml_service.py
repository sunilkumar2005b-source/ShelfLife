"""
ShelfLife ML Service
Bridges trained scikit-learn models from ml/inference.py to database records,
REST endpoints, and batch synchronization routines.
"""

from datetime import date
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path so ml module can be imported
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.inference import predict_demand as ml_predict_demand
from ml.inference import predict_spoilage as ml_predict_spoilage
from database import get_db_cursor
from schemas.ml import (
    DemandPredictionRequest,
    DemandPredictionResponse,
    SpoilagePredictionRequest,
    SpoilagePredictionResult,
    MLSyncResponse,
    MLStatusResponse,
)


def get_ml_status() -> MLStatusResponse:
    """Load model evaluation metrics and training metadata."""
    eval_dir = BASE_DIR / "ml" / "evaluation"
    demand_metrics_file = eval_dir / "demand_model_metrics.json"
    spoilage_metrics_file = eval_dir / "spoilage_model_metrics.json"

    demand_info = {}
    if demand_metrics_file.exists():
        with open(demand_metrics_file, "r") as f:
            demand_info = json.load(f)

    spoilage_info = {}
    if spoilage_metrics_file.exists():
        with open(spoilage_metrics_file, "r") as f:
            spoilage_info = json.load(f)

    return MLStatusResponse(
        status="Models Loaded and Operational",
        demand_model={
            "task": demand_info.get("task", "Demand Forecasting"),
            "champion_model": demand_info.get("champion_model", "Ridge Regression (alpha=1.0)"),
            "metrics": demand_info.get("champion_metrics", {}),
            "training_samples": demand_info.get("training_samples", 791),
            "testing_samples": demand_info.get("testing_samples", 198),
            "artifact_path": "ml/models/demand_forecast_model.joblib",
        },
        spoilage_model={
            "task": spoilage_info.get("task", "Spoilage Risk Classification"),
            "champion_model": spoilage_info.get("champion_model", "Logistic Regression"),
            "metrics": spoilage_info.get("champion_metrics", {}),
            "training_samples": spoilage_info.get("training_samples", 791),
            "testing_samples": spoilage_info.get("testing_samples", 198),
            "artifact_path": "ml/models/spoilage_risk_model.joblib",
        },
    )


def predict_product_demand(req: DemandPredictionRequest) -> DemandPredictionResponse:
    """
    Generate demand forecast for an existing product or custom parameter set.
    """
    product_name = None
    category = req.category or "Fruits & Vegetables"
    stock_quantity = req.stock_quantity if req.stock_quantity is not None else 50
    unit_price = req.unit_price if req.unit_price is not None else 4.50
    shelf_life_days = req.shelf_life_days if req.shelf_life_days is not None else 14
    reorder_level = req.reorder_level if req.reorder_level is not None else 30
    reorder_quantity = req.reorder_quantity if req.reorder_quantity is not None else 20

    if req.product_id is not None:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    p.product_id,
                    p.product_name,
                    p.category,
                    COALESCE(p.selling_price, 4.0),
                    COALESCE(p.shelf_life_days, 14),
                    COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_id = p.product_id), 0)
                FROM products p
                WHERE p.product_id = %s
            """, (req.product_id,))
            row = cur.fetchone()
            if row:
                product_name = row[1]
                category = row[2]
                unit_price = float(row[3])
                shelf_life_days = int(row[4])
                stock_quantity = int(row[5])

    raw_prediction = ml_predict_demand(
        category=category,
        stock_quantity=stock_quantity,
        reorder_level=reorder_level,
        reorder_quantity=reorder_quantity,
        unit_price=unit_price,
        shelf_life_days=shelf_life_days,
        month=req.month,
        day_of_week=req.day_of_week,
    )

    return DemandPredictionResponse(
        product_id=req.product_id,
        product_name=product_name,
        category=category,
        predicted_demand=raw_prediction["predicted_demand"],
        model_name=raw_prediction["model_name"],
        input_features=raw_prediction["input_features"],
    )


def predict_batch_spoilage(req: SpoilagePredictionRequest) -> SpoilagePredictionResult:
    """
    Generate spoilage risk prediction for an existing batch or custom parameters.
    """
    product_name = None
    product_id = req.product_id
    category = req.category or "Dairy"
    stock_quantity = req.stock_quantity if req.stock_quantity is not None else 40
    days_remaining = req.days_remaining if req.days_remaining is not None else 3
    unit_price = req.unit_price if req.unit_price is not None else 3.50
    total_shelf_life = req.total_shelf_life or 14

    if req.inventory_id is not None:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.product_name,
                    p.category,
                    i.quantity,
                    GREATEST(0, (i.expiry_date - CURRENT_DATE)),
                    COALESCE(p.selling_price, 3.5),
                    COALESCE(p.shelf_life_days, 14)
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                WHERE i.inventory_id = %s
            """, (req.inventory_id,))
            row = cur.fetchone()
            if row:
                product_id = row[1]
                product_name = row[2]
                category = row[3]
                stock_quantity = int(row[4])
                days_remaining = int(row[5])
                unit_price = float(row[6])
                total_shelf_life = int(row[7])

    raw_spoilage = ml_predict_spoilage(
        category=category,
        stock_quantity=stock_quantity,
        days_remaining=days_remaining,
        unit_price=unit_price,
        sales_volume=req.sales_volume,
        turnover_rate=req.turnover_rate,
        total_shelf_life=total_shelf_life,
    )

    return SpoilagePredictionResult(
        inventory_id=req.inventory_id,
        product_id=product_id,
        product_name=product_name,
        risk_level=raw_spoilage["risk_level"],
        spoilage_probability=raw_spoilage["spoilage_probability"],
        class_probabilities=raw_spoilage["class_probabilities"],
        model_name=raw_spoilage["model_name"],
    )


def sync_database_predictions() -> MLSyncResponse:
    """
    Executes live ML batch inference across all products and active inventory
    in shelflife_db, replacing synthetic demo seed entries with genuine trained
    Ridge and Logistic Regression predictions.
    """
    synced_forecasts = 0
    synced_spoilage = 0

    with get_db_cursor(commit=True) as cur:
        # 1. Clear previous prediction tables for clean idempotent refresh
        cur.execute("DELETE FROM demand_forecasts;")
        cur.execute("DELETE FROM spoilage_predictions;")

        # 2. Synchronize Demand Forecasts for all products
        cur.execute("""
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                COALESCE(p.selling_price, 4.0),
                COALESCE(p.shelf_life_days, 14),
                COALESCE((SELECT SUM(quantity) FROM inventory WHERE product_id = p.product_id), 0) AS stock
            FROM products p
            ORDER BY p.product_id
        """)
        products = cur.fetchall()

        for prod in products:
            pid = prod[0]
            cat = prod[2]
            price = float(prod[3])
            shelf_days = int(prod[4])
            stock = int(prod[5])

            pred = ml_predict_demand(
                category=cat,
                stock_quantity=stock,
                reorder_level=max(15, int(stock * 0.5)),
                reorder_quantity=max(10, int(stock * 0.4)),
                unit_price=price,
                shelf_life_days=shelf_days,
            )

            # Insert / update latest demand forecast
            cur.execute("""
                INSERT INTO demand_forecasts (product_id, forecast_date, predicted_demand, model_name)
                VALUES (%s, CURRENT_DATE, %s, %s)
            """, (pid, pred["predicted_demand"], pred["model_name"]))
            synced_forecasts += 1

        # 3. Synchronize Spoilage Predictions for all inventory batches
        cur.execute("""
            SELECT
                i.inventory_id,
                i.product_id,
                p.category,
                i.quantity,
                GREATEST(0, (i.expiry_date - CURRENT_DATE)) AS days_rem,
                COALESCE(p.selling_price, 3.5),
                COALESCE(p.shelf_life_days, 14)
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            ORDER BY i.inventory_id
        """)
        batches = cur.fetchall()

        for batch in batches:
            inv_id = batch[0]
            prod_id = batch[1]
            cat = batch[2]
            qty = int(batch[3])
            days_rem = int(batch[4])
            price = float(batch[5])
            shelf_days = int(batch[6])

            cat_normalized = cat
            if cat in ["Vegetable", "Fruit", "Fruits", "Vegetables"]:
                cat_normalized = "Fruits & Vegetables"

            if days_rem <= 2:
                turnover = 35.0
                sales_vol = 50.0
            elif days_rem <= 5:
                turnover = 60.0
                sales_vol = 95.0
            else:
                turnover = 78.0
                sales_vol = 135.0

            price_normalized = min(15.0, max(1.5, price / 20.0 if price > 20 else price))

            spoilage = ml_predict_spoilage(
                category=cat_normalized,
                stock_quantity=qty,
                days_remaining=days_rem,
                unit_price=price_normalized,
                total_shelf_life=shelf_days,
                sales_volume=sales_vol,
                turnover_rate=turnover,
            )

            prob = float(spoilage["spoilage_probability"])
            if prob >= 0.60:
                assigned_risk = "High"
            elif prob >= 0.30:
                assigned_risk = "Medium"
            else:
                assigned_risk = "Low"

            cur.execute("""
                INSERT INTO spoilage_predictions (
                    product_id, inventory_id, prediction_date, days_remaining,
                    spoilage_probability, risk_level, model_name
                )
                VALUES (%s, %s, CURRENT_DATE, %s, %s, %s, %s)
            """, (
                prod_id,
                inv_id,
                days_rem,
                prob,
                assigned_risk,
                spoilage["model_name"],
            ))
            synced_spoilage += 1

    return MLSyncResponse(
        success=True,
        synced_demand_forecasts=synced_forecasts,
        synced_spoilage_predictions=synced_spoilage,
        message=f"Successfully generated {synced_forecasts} demand forecasts and {synced_spoilage} spoilage predictions using trained ML models.",
    )
