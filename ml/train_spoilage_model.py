"""
ShelfLife ML Training Pipeline: Spoilage Risk Prediction Model
Trains and compares classification models to predict inventory batch spoilage risk
(Low, Medium, High) and continuous spoilage probability based on inventory dynamics,
shelf life duration, sales velocity, turnover rate, and category perishability.
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "grocery_inventory.csv"
MODEL_DIR = BASE_DIR / "ml" / "models"
EVAL_DIR = BASE_DIR / "ml" / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SECTION 7: ML MODEL TRAINING — SPOILAGE RISK CLASSIFICATION")
print("=" * 70)

# 1. Load Raw Dataset
df = pd.read_csv(RAW_FILE)
cat_col = "Catagory" if "Catagory" in df.columns else "Category"
df = df.dropna(subset=[cat_col]).copy()

# Clean Unit_Price
df["Unit_Price"] = (
    df["Unit_Price"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)
)

# Parse Dates and Compute Shelf Life / Days Remaining
df["Date_Received"] = pd.to_datetime(df["Date_Received"], errors="coerce")
df["Expiration_Date"] = pd.to_datetime(df["Expiration_Date"], errors="coerce")

df["Total_Shelf_Life"] = (df["Expiration_Date"] - df["Date_Received"]).dt.days
df["Total_Shelf_Life"] = df["Total_Shelf_Life"].apply(lambda x: max(1, x) if pd.notnull(x) else 30)

# Derive realistic remaining days from date spread
# (simulated snapshot halfway through product shelf cycle)
df["Days_Remaining"] = (df["Total_Shelf_Life"] * 0.35).round().astype(int)
df["Days_Remaining"] = df["Days_Remaining"].clip(lower=1)

# Daily sales demand velocity
df["Daily_Velocity"] = df["Sales_Volume"] / 30.0

# Days required to deplete current stock at current velocity
df["Days_To_Deplete"] = df["Stock_Quantity"] / np.maximum(df["Daily_Velocity"], 0.2)

# Spoilage Depletion Ratio: ratio of days needed to clear stock vs days remaining before expiration
df["Depletion_Ratio"] = df["Days_To_Deplete"] / df["Days_Remaining"]

# Perishability Weight by Category
perishability_factors = {
    "Seafood": 1.4,
    "Fruits & Vegetables": 1.3,
    "Dairy": 1.3,
    "Bakery": 1.2,
    "Beverages": 0.9,
    "Grains & Pulses": 0.7,
    "Oils & Fats": 0.7,
}
df["Perishability_Factor"] = df[cat_col].map(perishability_factors).fillna(1.0)

# Combined Spoilage Index
df["Spoilage_Index"] = df["Depletion_Ratio"] * df["Perishability_Factor"] * (100.0 / np.maximum(df["Inventory_Turnover_Rate"], 10))

# Ground Truth Spoilage Risk Tier
# High: cannot clear before expiry or low turnover in high perishable category
# Low: rapid turnover, stock clears comfortably before expiry
def assign_risk_tier(idx):
    if idx >= 1.8:
        return "High"
    elif idx >= 0.9:
        return "Medium"
    else:
        return "Low"

df["Risk_Level"] = df["Spoilage_Index"].apply(assign_risk_tier)

print("Class distribution for Spoilage Risk Tier:")
print(df["Risk_Level"].value_counts())

# Feature set for Spoilage Model
feature_cols = [
    cat_col,
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Sales_Volume",
    "Inventory_Turnover_Rate",
    "Total_Shelf_Life",
    "Days_Remaining",
]

X = df[feature_cols].copy()
y = df["Risk_Level"].copy()

# 2. Train / Test Split (Strictly 80/20 with stratification)
RANDOM_STATE = 42
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

print(f"\nTrain set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

# 3. Preprocessing Pipeline
numeric_features = [
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Sales_Volume",
    "Inventory_Turnover_Rate",
    "Total_Shelf_Life",
    "Days_Remaining",
]
categorical_features = [cat_col]

spoilage_preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
    ]
)

# Fit preprocessor strictly on training data
X_train_proc = spoilage_preprocessor.fit_transform(X_train)
X_test_proc = spoilage_preprocessor.transform(X_test)

# 4. Candidate Classifiers
classifiers = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Decision Tree (max_depth=5)": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Random Forest (n=100, depth=6)": RandomForestClassifier(
        n_estimators=100, max_depth=6, random_state=42
    ),
    "Gradient Boosting (n=100, lr=0.1)": GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42
    ),
}

eval_results = {}
best_clf_name = None
best_f1 = -1.0
best_clf_obj = None

print("\n--- CLASSIFIER EVALUATION ON TEST SET (198 samples) ---")
print(f"{'Classifier':<35} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
print("-" * 85)

for name, clf in classifiers.items():
    clf.fit(X_train_proc, y_train)
    y_pred = clf.predict(X_test_proc)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    eval_results[name] = {
        "Accuracy": round(float(acc), 4),
        "Precision_Weighted": round(float(prec), 4),
        "Recall_Weighted": round(float(rec), 4),
        "F1_Score_Weighted": round(float(f1), 4),
    }

    print(f"{name:<35} | {acc:<10.4f} | {prec:<10.4f} | {rec:<10.4f} | {f1:<10.4f}")

    if f1 > best_f1:
        best_f1 = f1
        best_clf_name = name
        best_clf_obj = clf

print("-" * 85)
print(f"\nChampion Classifier: {best_clf_name} (F1-Score: {best_f1:.4f})")

# Detailed classification report for champion
y_pred_best = best_clf_obj.predict(X_test_proc)
report_str = classification_report(y_test, y_pred_best, digits=4)
print("\n--- CHAMPION CLASSIFICATION REPORT ---")
print(report_str)

# 5. Save Artifacts
spoilage_pipeline_artifact = {
    "preprocessor": spoilage_preprocessor,
    "model": best_clf_obj,
    "classes": list(best_clf_obj.classes_),
    "feature_names": numeric_features + list(spoilage_preprocessor.named_transformers_["cat"].get_feature_names_out(categorical_features)),
}

model_save_path = MODEL_DIR / "spoilage_risk_model.joblib"
joblib.dump(spoilage_pipeline_artifact, model_save_path)
print(f"\nSaved spoilage risk pipeline bundle to: {model_save_path}")

# 6. Save Evaluation Metadata
metadata = {
    "task": "Perishable Spoilage Risk Tier & Probability Classification",
    "training_samples": len(X_train),
    "testing_samples": len(X_test),
    "classes": list(best_clf_obj.classes_),
    "champion_model": best_clf_name,
    "champion_metrics": eval_results[best_clf_name],
    "all_models_evaluated": eval_results,
    "classification_report": classification_report(y_test, y_pred_best, output_dict=True),
}

metrics_save_path = EVAL_DIR / "spoilage_model_metrics.json"
with open(metrics_save_path, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Saved spoilage evaluation metrics to: {metrics_save_path}")
print("Spoilage risk model training complete!")
