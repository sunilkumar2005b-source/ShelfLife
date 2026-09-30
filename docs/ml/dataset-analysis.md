# Machine Learning Dataset Analysis & Preprocessing Specification

## 1. Dataset Overview

- **Source File**: `data/raw/grocery_inventory.csv` (Real-world grocery inventory dataset)
- **Problem Formulation**: Supervised Machine Learning for Retail Demand Forecasting (`Sales_Volume`)
- **Total Raw Records**: 990 records, 17 columns
- **Cleaned Records**: 989 records (1 row dropped due to missing Category value)
- **Zero Synthetic Fabrication**: The dataset consists of genuine grocery inventory data tracking products, categories, stock, reorder levels, shelf life, and sales volumes across kirana/supermarket inventory categories.

---

## 2. Feature Schema & Data Dictionary

| Column Name | Raw Type | Cleaned Type | Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Catagory` | `str` | Categorical | Feature | Product category (`Fruits & Vegetables`, `Dairy`, `Grains & Pulses`, etc.) |
| `Stock_Quantity` | `int64` | Numeric | Feature | Units currently available on shelf |
| `Reorder_Level` | `int64` | Numeric | Feature | Minimum stock threshold triggering restock |
| `Reorder_Quantity`| `int64` | Numeric | Feature | Batch replenishment size |
| `Unit_Price` | `str` | Numeric (Float)| Feature | Retail price per unit in USD (stripped `$` currency symbol) |
| `Shelf_Life_Days` | Derived | Numeric (Days) | Feature | Duration in days from `Date_Received` to `Expiration_Date` |
| `Received_Month` | Derived | Numeric (1-12) | Feature | Seasonality month index extracted from `Date_Received` |
| `Received_DayOfWeek`| Derived| Numeric (0-6) | Feature | Weekly cycle index extracted from `Date_Received` |
| `Sales_Volume` | `int64` | Numeric (Units)| **Target** | Units demanded/sold (Demand Forecasting Target) |

---

## 3. Exploratory Data Analysis & Statistics

### 3.1 Target Variable (`Sales_Volume`)
- **Count**: 989 observations
- **Mean**: 58.95 units
- **Standard Deviation**: 23.00 units
- **Minimum**: 20 units
- **25th Percentile (Q1)**: 39.00 units
- **Median (50th Percentile)**: 58.00 units
- **75th Percentile (Q3)**: 78.00 units
- **Maximum**: 100 units
- **Distribution**: Uniform-Gaussian hybrid spanning 20 to 100 units, suitable for continuous regression and tree-based ensembles (e.g., Random Forest Regressor).

### 3.2 Category Distribution
| Category | Record Count | Percentage |
| :--- | :--- | :--- |
| **Fruits & Vegetables** | 331 | 33.47% |
| **Dairy** | 180 | 18.20% |
| **Grains & Pulses** | 162 | 16.38% |
| **Seafood** | 90 | 9.10% |
| **Oils & Fats** | 77 | 7.79% |
| **Beverages** | 75 | 7.58% |
| **Bakery** | 74 | 7.48% |
| **Total** | **989** | **100.0%** |

High concentration of perishable goods (`Fruits & Vegetables`, `Dairy`, `Bakery`, `Seafood` comprise over 68% of the inventory), aligning with ShelfLife's core perishable inventory problem statement.

---

## 4. Preprocessing & Data Leakage Prevention

To ensure scientific validity and prevent data leakage:
1. **Train/Test Split Before Transformation**:
   - Split: **80% Training (791 records)**, **20% Testing (198 records)**
   - Deterministic Split: `random_state=42`
2. **Standardization (`StandardScaler`)**:
   - Fitted strictly on `X_train` numeric features (`Stock_Quantity`, `Reorder_Level`, `Reorder_Quantity`, `Unit_Price`, `Shelf_Life_Days`, `Received_Month`, `Received_DayOfWeek`).
   - Mean and variance parameters calculated from training data only, then applied to `X_test`.
3. **One-Hot Encoding (`OneHotEncoder`)**:
   - Fitted strictly on `X_train["Catagory"]` with `handle_unknown="ignore"` to handle unseen categories at inference time.
   - Encoded 7 binary feature indicators: `Catagory_Bakery`, `Catagory_Beverages`, `Catagory_Dairy`, `Catagory_Fruits & Vegetables`, `Catagory_Grains & Pulses`, `Catagory_Oils & Fats`, `Catagory_Seafood`.

---

## 5. Generated Artifacts & Directory Structure

```
data/
├── inspect_and_preprocess.py       # Reproducible preparation script
├── raw/
│   └── grocery_inventory.csv       # Raw immutable input dataset
└── processed/
    ├── train_features.csv          # 791 rows x 14 preprocessed features
    ├── test_features.csv           # 198 rows x 14 preprocessed features
    ├── train_target.csv            # 791 target values (Sales_Volume)
    ├── test_target.csv             # 198 target values (Sales_Volume)
    ├── preprocessor.joblib         # Fitted scikit-learn ColumnTransformer
    └── dataset_metadata.json       # Metadata summary and feature registry
```

---

## 6. Verification & Reproducibility

To re-run the entire inspection and preprocessing pipeline deterministically:

```powershell
& "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\backend\venv\Scripts\python.exe" "C:\Users\SUNILKUMAR\OneDrive\Desktop\ShelfLife\data\inspect_and_preprocess.py"
```

The resulting pipeline guarantees identical feature matrix dimensions and value transformations ready for **Section 7: Machine Learning Model Training**.
