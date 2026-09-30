import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Paths
BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw" / "grocery_inventory.csv"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("SECTION 6: ML DATASET INSPECTION & PREPARATION")
print("=" * 60)

# 1. Load Raw Dataset
df = pd.read_csv(RAW_FILE)
print(f"Loaded raw dataset from: {RAW_FILE}")
print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n")

# 2. Inspect Columns and Types
print("--- COLUMNS & DATA TYPES ---")
for col, dtype in df.dtypes.items():
    print(f"  - {col}: {dtype}")

# 3. Missing Values
print("\n--- MISSING VALUES ---")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.sum() > 0 else "  Zero missing values detected across all columns.")

# 4. Duplicate Records
duplicates = df.duplicated().sum()
print(f"\n--- DUPLICATE RECORDS ---: {duplicates}")

# Clean Unit_Price: strip '$' and whitespace unconditionally
df["Unit_Price"] = (
    df["Unit_Price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.strip()
    .astype(float)
)
print("  Cleaned Unit_Price to numeric float.")

# Clean percentage: strip '%'
if "percentage" in df.columns:
    df["percentage"] = (
        df["percentage"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .astype(float)
    )
    print("  Cleaned percentage to numeric float.")

# Handle missing Category (1 record in dataset)
cat_col = "Catagory" if "Catagory" in df.columns else "Category"
initial_rows = len(df)
df = df.dropna(subset=[cat_col]).copy()
print(f"  Removed {initial_rows - len(df)} row(s) with missing {cat_col}. Remaining: {len(df)}")

# Parse dates and derive shelf life features
df["Date_Received"] = pd.to_datetime(df["Date_Received"], errors="coerce")
df["Expiration_Date"] = pd.to_datetime(df["Expiration_Date"], errors="coerce")
df["Last_Order_Date"] = pd.to_datetime(df["Last_Order_Date"], errors="coerce")

# Calculate total rated shelf life in days from received to expiration
df["Shelf_Life_Days"] = (df["Expiration_Date"] - df["Date_Received"]).dt.days
# Clip negative or erroneous shelf life values if any
df["Shelf_Life_Days"] = df["Shelf_Life_Days"].apply(lambda x: max(1, x) if pd.notnull(x) else np.nan)
df["Shelf_Life_Days"] = df["Shelf_Life_Days"].fillna(df["Shelf_Life_Days"].median())

# Extract date features
df["Received_Month"] = df["Date_Received"].dt.month
df["Received_DayOfWeek"] = df["Date_Received"].dt.dayofweek

print("  Derived Shelf_Life_Days, Received_Month, Received_DayOfWeek.")

# 6. Target Variable Analysis for Demand Forecasting
# Target: Sales_Volume (units demanded/sold)
print("\n--- TARGET VARIABLE ANALYSIS (Sales_Volume) ---")
target_col = "Sales_Volume"
y = df[target_col]
print(f"Target: {target_col}")
print(f"  Count: {len(y)}")
print(f"  Mean:  {y.mean():.2f}")
print(f"  Std:   {y.std():.2f}")
print(f"  Min:   {y.min()}")
print(f"  25%:   {y.quantile(0.25):.2f}")
print(f"  50%:   {y.median():.2f}")
print(f"  75%:   {y.quantile(0.75):.2f}")
print(f"  Max:   {y.max()}")

# 7. Categorical Distribution
print("\n--- CATEGORY DISTRIBUTION ---")
cat_col = "Catagory" if "Catagory" in df.columns else "Category"
print(df[cat_col].value_counts())

# 8. Feature Selection for Demand Forecasting Model
feature_cols = [
    cat_col,
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Shelf_Life_Days",
    "Received_Month",
    "Received_DayOfWeek",
]

X = df[feature_cols].copy()
y = df[target_col].copy()

print(f"\nSelected {len(feature_cols)} features: {feature_cols}")

# 9. Train / Test Split (Strictly before transformations to avoid data leakage)
RANDOM_STATE = 42
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE
)
print(f"\nTrain set: {X_train.shape[0]} samples (80%)")
print(f"Test set:  {X_test.shape[0]} samples (20%)")

# 10. Fit Preprocessing Pipeline ONLY on Training Data
numeric_features = [
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Shelf_Life_Days",
    "Received_Month",
    "Received_DayOfWeek",
]
categorical_features = [cat_col]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
    ]
)

# Fit on training data ONLY
preprocessor.fit(X_train)
print("Fitted ColumnTransformer (StandardScaler + OneHotEncoder) strictly on X_train.")

# Transform both train and test
X_train_processed = preprocessor.transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Retrieve transformed feature names
cat_encoder = preprocessor.named_transformers_["cat"]
encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
all_feature_names = numeric_features + encoded_cat_names

X_train_df = pd.DataFrame(X_train_processed, columns=all_feature_names)
X_test_df = pd.DataFrame(X_test_processed, columns=all_feature_names)

# 11. Save Processed Artifacts
X_train_df.to_csv(PROCESSED_DIR / "train_features.csv", index=False)
X_test_df.to_csv(PROCESSED_DIR / "test_features.csv", index=False)
y_train.to_csv(PROCESSED_DIR / "train_target.csv", index=False)
y_test.to_csv(PROCESSED_DIR / "test_target.csv", index=False)

# Save fitted preprocessor
joblib.dump(preprocessor, PROCESSED_DIR / "preprocessor.joblib")
print(f"\nSaved preprocessor to: {PROCESSED_DIR / 'preprocessor.joblib'}")

# Save detailed metadata
metadata = {
    "dataset_source": "data/raw/grocery_inventory.csv",
    "total_rows": int(df.shape[0]),
    "total_raw_columns": int(df.shape[1]),
    "cleaned_rows": int(df.shape[0]),
    "train_samples": int(X_train.shape[0]),
    "test_samples": int(X_test.shape[0]),
    "random_seed": RANDOM_STATE,
    "target_variable": target_col,
    "target_mean": float(y.mean()),
    "target_std": float(y.std()),
    "target_min": float(y.min()),
    "target_max": float(y.max()),
    "features_count": len(all_feature_names),
    "features_list": all_feature_names,
    "categories": df[cat_col].unique().tolist(),
}

with open(PROCESSED_DIR / "dataset_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Saved dataset metadata to: {PROCESSED_DIR / 'dataset_metadata.json'}")
print("Preprocessed files saved successfully under data/processed/!")
