# ShelfLife: AI-Powered Perishable Inventory Management and Retail Analytics System

> **Final-Year Integrated M.Tech Software Engineering Project**  
> **Domain:** Applied Machine Learning / Retail Supply Chain Analytics / Decision Support Systems  
> **Tech Stack:** PostgreSQL 18, FastAPI (Python 3.13), React 19 + Vite 8, scikit-learn, joblib

---

## 1. Project Overview

**ShelfLife** is an enterprise-grade full-stack perishable inventory management and predictive retail intelligence system developed for small retail stores, kirana shops, and neighbourhood supermarkets.

Perishable products (dairy, vegetables, fruits, bakery, meat) experience aggressive shelf-life decay and volatile demand. ShelfLife combines **physical batch-level tracking**, **supervised machine learning**, and a **deterministic multi-factor rule engine** to prevent spoilage, eliminate stockouts, and salvage capital through dynamic clearance markdowns.

---

## 2. Key Capabilities & Engineering Features

- **Executive Command Center:** Real-time visibility into active stock, imminent expiries, spoilage exposure, and composite inventory health.
- **Faculty Demonstration Scenarios:** Instant stress simulation of extreme weather shocks (*Heatwave 41.5°C*), demand spikes (*Stockout Crisis*), and bulk expiration waves (*Urgent Clearance*).
- **Supervised Machine Learning:**
  - **Demand Forecasting:** Ridge Regression ($L_2$ Regularized, $\alpha=1.0$) predicting continuous consumer demand units (MAE: 19.45, RMSE: 22.75 units).
  - **Spoilage Risk Radar:** Cost-Sensitive Logistic Regression calculating batch degradation probabilities (88.89% Accuracy, 96.03% High-Risk Recall).
- **Deterministic Decision Engine:** Calculates a 0–100 composite **Inventory Health Score** and outputs prescriptive interventions: *Urgent Clearance*, *Sell Quickly*, *Reorder*, *Monitor Stock*, or *Sufficient Stock*.
- **Financial Valuation & Markdown Simulator:** Live assessment of capital at risk and interactive promotional salvage modeling.
- **Enterprise CSV Audits:** Streaming export of full inventory audits and degradation assessments.
- **100% Automated Test Coverage:** 33 unit and integration tests verifying APIs, ML pipelines, heuristics, and reports.

---

## 3. Technology Stack & Environment

| Layer | Technologies | Role in System |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite 8, Modern CSS (Plus Jakarta Sans) | Responsive SPA dashboard, interactive simulators, sortable tables, and toast system |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic | High-performance asynchronous REST microservice APIs and auto OpenAPI docs (`/docs`) |
| **Machine Learning** | scikit-learn, pandas, NumPy, joblib | Continuous demand regression, probabilistic degradation classification, pipeline serialization |
| **Database** | PostgreSQL 18.x (`shelflife_db`) | ACID relational persistence, foreign key constraints (`ON DELETE CASCADE`), B-tree indexes |
| **Testing** | Python `unittest` | 33 automated tests across 5 test suites |
| **Platform** | Windows 10 / 11 (PowerShell & Batch) | Native one-click startup and management automation scripts |

---

## 4. Directory Structure

```text
ShelfLife/
├── start-shelflife.bat          # One-click Windows batch launcher (Backend + Frontend)
├── start-shelflife.ps1          # One-click PowerShell launcher with DB check
├── stop-shelflife.bat           # Graceful shutdown batch script
├── stop-shelflife.ps1           # Graceful shutdown PowerShell script
├── run-tests.bat                # Automated test runner batch script
├── run-tests.ps1                # Full 33-test verification suite with report
├── seed-demo.bat                # Demo reset batch script
├── seed-demo.ps1                # Scenario reset PowerShell script
├── README.md                    # Master project documentation
├── docs/                        # In-depth technical specifications
│   ├── defense/                 # Master Faculty Defense Guide & Viva Voce Q&A
│   ├── architecture/            # Architectural overview and layer diagrams
│   ├── api/                     # REST API & ML specification
│   ├── database/                # Schema, ER diagrams, sample SQL
│   ├── frontend/                # UI design system & view specifications
│   ├── intelligence/            # Rule engine heuristics & decision boundaries
│   └── ml/                      # Dataset analysis & model benchmark report
├── data/                        # Datasets (raw & preprocessed features)
├── ml/                          # Trained models, encoders & inference scripts
│   ├── models/                  # demand_forecast_model.joblib, spoilage_risk_model.joblib
│   └── preprocessor.joblib      # StandardScaler & OneHotEncoder pipeline
├── backend/                     # FastAPI Application
│   ├── main.py                  # API routes, middleware & startup hooks
│   ├── database.py              # PostgreSQL connection provider
│   ├── rule_engine.py           # Deterministic inventory health engine
│   ├── routes/                  # Modular REST routers (products, inventory, ml, reports, demo)
│   └── tests/                   # 33 unit and integration test cases
└── frontend/                    # React 19 Client
    ├── src/
    │   ├── App.jsx              # Master shell, navigation, and toast system
    │   ├── App.css              # Enterprise design system & responsive styling
    │   ├── index.css            # Base stylesheet & design tokens
    │   └── components/          # Modular views and interactive modal simulators
    ├── package.json
    └── vite.config.js
```

---

## 5. One-Click Quick Start (Windows)

### Option A: Double-Click Launcher
Simply double-click **`start-shelflife.bat`** in the project root!  
It automatically:
1. Verifies PostgreSQL connectivity (port 5432).
2. Activates the Python virtual environment and launches FastAPI (`http://127.0.0.1:8000`).
3. Launches the Vite frontend (`http://localhost:5173`).
4. Automatically opens your default web browser to the dashboard!

### Option B: PowerShell Commands
```powershell
# Launch all services:
.\start-shelflife.ps1

# Run the full 33-test suite:
.\run-tests.ps1

# Reset to baseline demo state:
.\seed-demo.ps1

# Stop all running services:
.\stop-shelflife.ps1
```

---

## 6. Machine Learning Architecture & Benchmark Metrics

| Model Architecture | Task | Key Metric | Validation Score | Champion Selection Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Ridge Regression ($\alpha=1.0$)** | Demand Forecast | RMSE / MAE | **22.75 / 19.45** | **Champion:** Prevents collinearity variance between stock quantity and reorder levels. |
| Ordinary Least Squares (OLS) | Demand Forecast | RMSE / MAE | 23.41 / 20.12 | Vulnerable to correlated grocery inventory predictors. |
| Random Forest Regressor | Demand Forecast | RMSE / MAE | 26.80 / 22.30 | Prone to overfitting on smaller grocery categories; higher latency. |
| **Logistic Regression (Class-Weighted)** | Spoilage Risk | Accuracy / Recall | **88.89% / 96.03%** | **Champion:** 96.03% Recall ensures near-zero false negatives for spoiled perishables. |
| Decision Tree Classifier | Spoilage Risk | Accuracy / Recall | 84.34% / 88.10% | Step-function splits lack smooth probabilistic confidence scores. |

---

## 7. Master REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API availability greeting |
| `GET` | `/health` | Health probe (database + service status) |
| `GET` | `/products` | List all cataloged perishables |
| `POST` | `/products` | Create a new product and auto-trigger ML predictions |
| `GET` | `/inventory` | List physical inventory batches with expiry dates |
| `POST` | `/inventory` | Record new inventory batch and evaluate spoilage risk |
| `GET` | `/ml/status` | Active ML models, preprocessor status, and benchmark metrics |
| `POST` | `/ml/predict/demand` | On-demand continuous demand forecasting |
| `POST` | `/ml/predict/spoilage` | On-demand spoilage risk probability classification |
| `POST` | `/ml/sync-predictions` | Re-run trained models across all database records |
| `GET` | `/dashboard-summary` | Aggregated dashboard KPI counts and risk metrics |
| `GET` | `/inventory-intelligence` | Multi-factor health scores, rules, and decision explanations |
| `GET` | `/reports/financial-risk` | Real-time valuation of perishable capital at risk |
| `POST` | `/reports/simulate-clearance` | Dynamic promotional markdown salvage simulation |
| `GET` | `/reports/inventory-audit.csv` | Download streaming CSV inventory audit log |
| `GET` | `/reports/spoilage-risk.csv` | Download streaming CSV spoilage risk evaluation |
| `POST` | `/demo/apply-scenario` | Inject demo presets (`normal`, `heatwave`, `urgent_clearance`, `stockout_crisis`) |

Interactive Swagger UI: **`http://127.0.0.1:8000/docs`**

---

## 8. Faculty Defense Guide

A complete, formal academic defense manual is provided at:  
- **[`docs/defense/faculty-defense-guide.md`](docs/defense/faculty-defense-guide.md)**

It includes:
- **Mathematical Formulations:** KaTeX-rendered equations for Ridge $L_2$ penalties, Logistic binary cross-entropy, and the composite inventory health formula.
- **5-Minute Live Presentation Script:** Step-by-step walkthrough covering what to click, what to show, and what to say during defense.
- **Top 25 Viva Voce Questions & Authoritative Answers:** Covering system architecture, database ACID guarantees, machine learning rigor, and supply chain heuristics.
