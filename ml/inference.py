"""
ShelfLife ML Inference Service
Provides a clean, modular Python API to generate real-time predictions using
the trained Demand Forecasting and Spoilage Risk models.
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional
import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEMAND_MODEL_PATH = BASE_DIR / "ml" / "models" / "demand_forecast_model.joblib"
DEMAND_PREPROCESSOR_PATH = BASE_DIR / "data" / "processed" / "preprocessor.joblib"
SPOILAGE_BUNDLE_PATH = BASE_DIR / "ml" / "models" / "spoilage_risk_model.joblib"

# Module-level cached models
_demand_model = None
_demand_preprocessor = None
_spoilage_bundle = None


def load_demand_pipeline():
    """Load demand forecasting model and preprocessor (cached)."""
    global _demand_model, _demand_preprocessor
    if _demand_model is None:
        if not DEMAND_MODEL_PATH.exists() or not DEMAND_PREPROCESSOR_PATH.exists():
            raise FileNotFoundError(
                f"Demand model artifacts not found at {DEMAND_MODEL_PATH} or {DEMAND_PREPROCESSOR_PATH}"
            )
        _demand_model = joblib.load(DEMAND_MODEL_PATH)
        _demand_preprocessor = joblib.load(DEMAND_PREPROCESSOR_PATH)
    return _demand_model, _demand_preprocessor


def load_spoilage_pipeline():
    """Load spoilage risk classification pipeline bundle (cached)."""
    global _spoilage_bundle
    if _spoilage_bundle is None:
        if not SPOILAGE_BUNDLE_PATH.exists():
            raise FileNotFoundError(f"Spoilage model artifact not found at {SPOILAGE_BUNDLE_PATH}")
        _spoilage_bundle = joblib.load(SPOILAGE_BUNDLE_PATH)
    return _spoilage_bundle


def predict_demand(
    category: str,
    stock_quantity: int = 50,
    reorder_level: int = 30,
    reorder_quantity: int = 20,
    unit_price: float = 4.5,
    shelf_life_days: int = 14,
    month: Optional[int] = None,
    day_of_week: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Predict expected sales volume / demand for a perishable product using the trained Ridge Regression model.
    """
    model, preprocessor = load_demand_pipeline()

    today = date.today()
    month = month if month is not None else today.month
    day_of_week = day_of_week if day_of_week is not None else today.weekday()

    raw_df = pd.DataFrame(
        [
            {
                "Catagory": category,
                "Stock_Quantity": int(stock_quantity),
                "Reorder_Level": int(reorder_level),
                "Reorder_Quantity": int(reorder_quantity),
                "Unit_Price": float(unit_price),
                "Shelf_Life_Days": int(shelf_life_days),
                "Received_Month": int(month),
                "Received_DayOfWeek": int(day_of_week),
            }
        ]
    )

    X_transformed = preprocessor.transform(raw_df)
    numeric_features = [
        "Stock_Quantity",
        "Reorder_Level",
        "Reorder_Quantity",
        "Unit_Price",
        "Shelf_Life_Days",
        "Received_Month",
        "Received_DayOfWeek",
    ]
    encoded_cat = preprocessor.named_transformers_["cat"].get_feature_names_out(["Catagory"]).tolist()
    X_df = pd.DataFrame(X_transformed, columns=numeric_features + encoded_cat)

    predicted_units = float(model.predict(X_df)[0])
    # Demand is strictly non-negative
    predicted_units = max(0.0, round(predicted_units, 2))

    return {
        "predicted_demand": predicted_units,
        "model_name": "Ridge Regression (Trained ML)",
        "input_features": {
            "category": category,
            "stock_quantity": stock_quantity,
            "reorder_level": reorder_level,
            "reorder_quantity": reorder_quantity,
            "unit_price": unit_price,
            "shelf_life_days": shelf_life_days,
            "month": month,
            "day_of_week": day_of_week,
        },
    }


def predict_spoilage(
    category: str,
    stock_quantity: int,
    days_remaining: int,
    reorder_level: int = 30,
    reorder_quantity: int = 20,
    unit_price: float = 4.5,
    sales_volume: Optional[float] = None,
    turnover_rate: Optional[float] = None,
    total_shelf_life: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Predict spoilage probability and risk level for an inventory batch using the trained Logistic Regression model.
    """
    bundle = load_spoilage_pipeline()
    preprocessor = bundle["preprocessor"]
    model = bundle["model"]
    classes = list(bundle["classes"])

    # Fallbacks for missing optional retail metrics
    sales_volume = float(sales_volume) if sales_volume is not None else 55.0
    turnover_rate = float(turnover_rate) if turnover_rate is not None else 50.0
    total_shelf_life = int(total_shelf_life) if total_shelf_life is not None else max(int(days_remaining) * 2, 7)

    raw_df = pd.DataFrame(
        [
            {
                "Catagory": category,
                "Stock_Quantity": int(stock_quantity),
                "Reorder_Level": int(reorder_level),
                "Reorder_Quantity": int(reorder_quantity),
                "Unit_Price": float(unit_price),
                "Sales_Volume": float(sales_volume),
                "Inventory_Turnover_Rate": float(turnover_rate),
                "Total_Shelf_Life": int(total_shelf_life),
                "Days_Remaining": int(days_remaining),
            }
        ]
    )

    X_proc = preprocessor.transform(raw_df)
    predicted_risk = str(model.predict(X_proc)[0])

    probabilities = model.predict_proba(X_proc)[0]
    prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probabilities)}

    # High risk probability represents spoilage risk probability
    spoilage_prob = prob_dict.get("High", 0.0)
    # If predicted is medium, probability should reflect partial risk
    if predicted_risk == "Medium" and spoilage_prob < 0.40:
        spoilage_prob = round(float(prob_dict.get("Medium", 0.5) * 0.5 + spoilage_prob), 4)

    return {
        "risk_level": predicted_risk,
        "spoilage_probability": min(1.0, max(0.0, spoilage_prob)),
        "class_probabilities": prob_dict,
        "model_name": "Logistic Regression (Trained ML)",
    }


if __name__ == "__main__":
    print("Testing ML inference pipeline on sample inputs...")
    sample_demand = predict_demand(
        category="Fruits & Vegetables",
        stock_quantity=45,
        reorder_level=20,
        reorder_quantity=25,
        unit_price=3.20,
        shelf_life_days=10,
    )
    print("Sample Demand Prediction:", sample_demand)

    sample_spoilage = predict_spoilage(
        category="Dairy",
        stock_quantity=60,
        days_remaining=2,
        reorder_level=25,
        reorder_quantity=20,
        unit_price=4.50,
        sales_volume=40,
        turnover_rate=30,
        total_shelf_life=14,
    )
    print("Sample Spoilage Prediction:", sample_spoilage)
