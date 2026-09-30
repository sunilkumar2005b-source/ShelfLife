"""
ShelfLife ML Training Pipeline: Demand Forecasting Model
Compares multiple regression algorithms on genuine grocery inventory data.
Evaluates on held-out test set using MAE, RMSE, R2, and MAPE.
Saves the champion model and evaluation metrics.
"""

import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "ml" / "models"
EVAL_DIR = BASE_DIR / "ml" / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SECTION 7: ML MODEL TRAINING — DEMAND FORECASTING REGRESSION")
print("=" * 70)

# 1. Load Preprocessed Datasets
X_train = pd.read_csv(DATA_DIR / "train_features.csv")
X_test = pd.read_csv(DATA_DIR / "test_features.csv")
y_train = pd.read_csv(DATA_DIR / "train_target.csv").squeeze("columns")
y_test = pd.read_csv(DATA_DIR / "test_target.csv").squeeze("columns")

print(f"Loaded train features: {X_train.shape} | target: {y_train.shape}")
print(f"Loaded test features:  {X_test.shape}  | target: {y_test.shape}")
print(f"Feature columns ({len(X_train.columns)}): {list(X_train.columns)}\n")

# 2. Candidate Regression Models
candidates = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression (alpha=1.0)": Ridge(alpha=1.0, random_state=42),
    "Decision Tree (max_depth=5)": DecisionTreeRegressor(max_depth=5, random_state=42),
    "Random Forest (n=100, depth=8)": RandomForestRegressor(
        n_estimators=100, max_depth=8, min_samples_split=4, random_state=42
    ),
    "Gradient Boosting (n=100, lr=0.08)": GradientBoostingRegressor(
        n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42
    ),
}

results = {}
best_model_name = None
best_rmse = float("inf")
best_model_obj = None

print("--- MODEL TRAINING & EVALUATION ON TEST SET (198 samples) ---")
print(f"{'Model Name':<36} | {'MAE':<8} | {'RMSE':<8} | {'R2 Score':<9} | {'MAPE (%)':<8}")
print("-" * 78)

for name, model in candidates.items():
    # Fit model on training data
    model.fit(X_train, y_train)

    # Predict on unseen test set
    y_pred = model.predict(X_test)

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    # MAPE calculation (avoid division by 0)
    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100

    results[name] = {
        "MAE": round(float(mae), 4),
        "RMSE": round(float(rmse), 4),
        "R2_Score": round(float(r2), 4),
        "MAPE_Percent": round(float(mape), 2),
    }

    print(f"{name:<36} | {mae:<8.2f} | {rmse:<8.2f} | {r2:<9.4f} | {mape:<8.2f}%")

    if rmse < best_rmse:
        best_rmse = rmse
        best_model_name = name
        best_model_obj = model

print("-" * 78)
print(f"\nChampion Model: {best_model_name} (Lowest Test RMSE: {best_rmse:.2f})")

# 3. Feature Importance Analysis (if tree-based)
feature_importances = {}
if hasattr(best_model_obj, "feature_importances_"):
    importances = best_model_obj.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("\n--- FEATURE IMPORTANCES ---")
    for i in sorted_idx:
        fname = X_train.columns[i]
        fimp = float(importances[i])
        feature_importances[fname] = round(fimp, 4)
        print(f"  {fname:<30}: {fimp * 100:.2f}%")

# 4. Save Champion Model Artifact
champion_path = MODEL_DIR / "demand_forecast_model.joblib"
joblib.dump(best_model_obj, champion_path)
print(f"\nSaved champion model artifact to: {champion_path}")

# 5. Save Evaluation Report to JSON
eval_metadata = {
    "task": "Perishable Demand Forecasting (Sales Volume Regression)",
    "training_samples": len(X_train),
    "testing_samples": len(X_test),
    "features_count": len(X_train.columns),
    "features": list(X_train.columns),
    "champion_model": best_model_name,
    "champion_metrics": results[best_model_name],
    "all_models_evaluated": results,
    "feature_importances": feature_importances,
}

eval_file = EVAL_DIR / "demand_model_metrics.json"
with open(eval_file, "w") as f:
    json.dump(eval_metadata, f, indent=2)
print(f"Saved evaluation metrics to: {eval_file}")
print("Demand forecasting training complete!")
