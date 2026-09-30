# Advanced Analytics, Financial Waste Modeling & Faculty Demo Specification

## 1. Overview
In **Section 9**, the ShelfLife system extends beyond heuristic and predictive machine learning models into **actionable executive decision support**, financial valuation, and an interactive faculty demonstration suite:
- **Financial Waste & Valuation Engine**: Translates physical inventory units into exact dollar amounts, calculating total capital invested, capital at high spoilage risk, and potential lost retail profit margins.
- **Clearance Markdown Recovery Simulator**: Dynamically models revenue salvaged by applying early promotional discounts ($20\% - 50\%$) on deteriorating batches compared to suffering total loss.
- **Exportable Audit Reports**: Provides one-click CSV data streaming for stockroom inventory audits and spoilage risk monitoring.
- **Faculty Evaluation Scenario Engine**: Enables evaluators and defense committees to stress-test the AI engine across 4 preset retail events in real time.

---

## 2. Financial Waste & Capital-at-Risk Mathematics

### 2.1 Inventory Valuation
$$\text{Cost Valuation} = \sum_{i=1}^{N} \left( Q_i \times C_i \right)$$
$$\text{Potential Retail Revenue} = \sum_{i=1}^{N} \left( Q_i \times P_i \right)$$
$$\text{Potential Gross Margin} = \text{Potential Retail Revenue} - \text{Cost Valuation}$$
Where:
- $Q_i$: Quantity of batch $i$ currently in stock.
- $C_i$: Purchase cost price per unit.
- $P_i$: Regular retail selling price per unit.

### 2.2 Capital at High Spoilage Risk
$$\text{Capital at Risk} = \sum_{i \in \text{High Risk}} \left( Q_i \times C_i \right)$$
$$\text{Risk Exposure Percentage} = \frac{\text{Capital at Risk}}{\text{Cost Valuation}} \times 100$$
$$\text{Projected Lost Profit Margin} = \sum_{i \in \text{High Risk}} Q_i \times (P_i - C_i)$$

### 2.3 Promotional Markdown Salvage Formulation
If a retailer applies a promotional discount $\delta \in [0.10, 0.70]$ on an at-risk batch before expiration:
$$\text{Salvaged Revenue} = \sum_{i \in \text{High Risk}} \left( Q_i \times P_i \times (1 - \delta) \right)$$
$$\text{Net Avoided Loss} = \text{Salvaged Revenue} - \text{Cost Valuation}_{\text{High Risk}}$$
Even at a 30% discount ($\delta = 0.30$), the store rescues significant capital and customer goodwill instead of recording a 100% write-off.

---

## 3. Faculty Demonstration Scenarios

The system embeds an interactive scenario switcher allowing evaluators to simulate retail volatility with one click:

| Preset Scenario | Environmental State | Inventory Alterations | AI/ML System Reaction |
| :--- | :--- | :--- | :--- |
| **☀️ Normal State** | Ambient: 24.0°C, Humidity: 55% | Balanced stock, staggered expiration (4–90 days) | High Health Scores (70–95%), baseline demand predictions |
| **🔥 Heatwave Crisis** | Ambient: 41.5°C, Humidity: 88% | Storage temp elevated to 12°C in non-refrigerated batches | Cold-chain violations trigger immediate penalty subtractions; Dairy health drops to Critical; ambient decay alerts appear |
| **⚡ Bulk Expiration** | Ambient: Normal | 5 perishable batches forced to expire in 24 hours | Spoilage probabilities surge to 99%; rule engine triggers immediate "Clearance Action" warnings |
| **⚠️ Stockout Shortfall** | Ambient: Normal | Top items (Milk, Tomatoes) stock reduced to 2 units | Stock ratio drops below 0.10; system flags critical stockout alert and calculates exact replenishment batch |

---

## 4. Exportable Reports Specification

### 4.1 Inventory Audit CSV (`GET /reports/inventory-audit.csv`)
Streams a production-ready audit sheet:
- Columns: `Batch ID, Product ID, Product Name, Category, Batch Number, Quantity On Hand, Unit, Cost Price ($), Total Cost Valuation ($), Selling Price ($), Potential Retail Revenue ($), Purchase Date, Expiry Date, Days Remaining, Storage Temp (°C), Spoilage Probability (%), Risk Tier, Forecasted Demand (Units)`
- HTTP Headers: `Content-Type: text/csv`, `Content-Disposition: attachment; filename=shelflife_inventory_audit.csv`

### 4.2 Spoilage Risk CSV (`GET /reports/spoilage-risk.csv`)
Focused audit for waste control:
- Columns: `Prediction ID, Product Name, Category, Batch ID, Batch Number, Quantity, Unit Cost ($), Capital At Risk ($), Days Remaining, Spoilage Probability (%), Risk Tier, Model Provenance, Prediction Date`
- HTTP Headers: `Content-Type: text/csv`, `Content-Disposition: attachment; filename=shelflife_spoilage_risk.csv`

---

## 5. Verification & Test Coverage
The suite is verified by `backend/tests/test_reports.py` and the master regression runner:
- **33 Automated Unit & Integration Tests Passing (100% OK)**
- Verified live on FastAPI (`http://127.0.0.1:8000`) and React Vite (`http://localhost:5173`).
