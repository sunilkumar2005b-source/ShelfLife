# ShelfLife React Frontend & Dashboard Specification

## 1. Frontend Architecture Overview

The **ShelfLife** user interface is built as a single-page application using **React 19** and bundled with **Vite 8**. It provides small retail store operators with a responsive, high-contrast, faculty-demo-ready command center for perishable inventory management.

- **Dev Server URL:** `http://localhost:5173`
- **Component Model:** Functional components with React hooks (`useState`, `useEffect`, `useMemo`)
- **Backend API Integration:** Dynamic REST communications with FastAPI at `http://127.0.0.1:8000` via native fetch APIs
- **Design System:** Custom responsive CSS design system in `App.css` featuring emerald branding (`#0d3b2e`, `#138a5b`), rounded status pills, color-coded health meters, and modal dialogs.

---

## 2. Component Hierarchy

```text
src/
├── main.jsx                       # Application DOM root mount
├── index.css                      # Global baseline stylesheet
├── App.css                        # Design system & responsive layouts
├── App.jsx                        # Master state manager, header & navigation router
└── components/                    # Modular view components
    ├── DashboardView.jsx          # KPI stat cards, risk distributions & urgent alerts
    ├── ProductsView.jsx           # Products table with search, category filter & supplier info
    ├── InventoryView.jsx          # Batch-level inventory with expiry countdowns & freshness badges
    ├── SpoilageView.jsx           # Spoilage probability progress bars & risk tiers
    ├── ForecastView.jsx           # Historical sales vs forecasted demand with demo disclosure
    ├── IntelligenceView.jsx       # Health score visual meters & rule-based action recommendations
    ├── AddProductModal.jsx        # Interactive modal form submitting POST /products
    └── AddInventoryModal.jsx      # Interactive modal form submitting POST /inventory
```

---

## 3. View Specifications

### 3.1 Executive Dashboard (`DashboardView.jsx`)
- **6 Real-Time Stat Cards:**
  1. *Total Products:* Distinct perishable items cataloged.
  2. *Total Stock Units:* Total physical units currently held across all batches.
  3. *Expiring Soon:* Batches with $\le 3$ days remaining before expiry (highlighted in red/yellow).
  4. *High Spoilage Risk:* Number of batches assessed as high spoilage risk.
  5. *Low Stock Items:* Items where stock is insufficient relative to forecasted demand or below safe buffer levels.
  6. *Inventory Health:* Store-wide aggregate inventory health percentage.
- **Spoilage Risk Distribution:** Visual cards segmenting high, medium, and low risk batches.
- **Demand Forecast Summary:** Top forecasted items compared against on-hand inventory.
- **Immediate Attention Alert Table:** Filtered list of products requiring urgent clearance or rapid selling.

### 3.2 Products Catalog (`ProductsView.jsx`)
- **Interactive Features:** Real-time search by product title and category drop-down filter (`Dairy`, `Bakery`, `Vegetable`, `Fruit`).
- **Data Table:** ID, Product Name, Category badge, Unit, Purchase Price (₹), Selling Price (₹), Shelf Life (days), Primary Supplier attribution.
- **Actions:** Modal button to add new perishable products directly calling `POST /products`.

### 3.3 Inventory Batches (`InventoryView.jsx`)
- **Tracking:** Batch Code, Product, Category, Quantity in stock, Purchase Date, Expiry Date, Storage Temperature (°C), Days Remaining.
- **Status Badges:**
  - `Fresh / Good`: Safe shelf life ($> 5$ days).
  - `Expiring Soon`: Approaching expiry ($3 - 5$ days).
  - `Urgent`: Imminent expiry ($\le 2$ days).
  - `Expired`: $0$ days remaining.
- **Actions:** Modal button to create new inventory batches calling `POST /inventory`.

### 3.4 Spoilage Risk Analysis (`SpoilageView.jsx`)
- **Visuals:** Visual horizontal progress meters depicting spoilage probability ($0\% - 100\%$).
- **Risk Tiers:** Color-coded badges for High, Medium, and Low risk tiers.
- **Academic Transparency:** Explicit banner stating probabilities originate from synthetic demonstration data pending supervised model training.

### 3.5 Demand Forecasting (`ForecastView.jsx`)
- **Sales Comparison:** Aggregates real historical sales units from POS transactions alongside projected demand units.
- **Transparency Notice:** Clearly displays model attribution and labels demo seed records.

### 3.6 Inventory Intelligence (`IntelligenceView.jsx`)
- **Recommendation Summary Cards:** Interactive category pills showing counts for *Urgent Clearance*, *Sell Quickly*, *Reorder*, *Monitor Stock*, and *Sufficient Stock*.
- **Multi-Factor Intelligence Table:**
  - Product Name
  - Days Remaining
  - Current Stock vs Predicted Demand
  - Spoilage Risk Tier
  - Health Score (0-100) with visual meter track
  - Color-coded Action Recommendation badge
  - Natural Language Decision Explanation detailing the exact heuristic rationale.
