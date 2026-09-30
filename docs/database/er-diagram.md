# ShelfLife Entity-Relationship (ER) Diagram

The following diagram represents the relational data model for **ShelfLife** deployed on PostgreSQL (`shelflife_db`).

```mermaid
erDiagram
    PRODUCTS ||--o{ INVENTORY : "stocked as"
    PRODUCTS ||--o{ SALES : "sold via"
    PRODUCTS ||--o{ PURCHASE_ORDERS : "ordered via"
    PRODUCTS ||--o{ DEMAND_FORECASTS : "forecasted in"
    PRODUCTS ||--o{ SPOILAGE_PREDICTIONS : "assessed in"
    PRODUCTS ||--o{ ANALYTICS : "aggregated in"
    
    SUPPLIERS ||--o{ PURCHASE_ORDERS : "supplies"
    INVENTORY ||--o{ SPOILAGE_PREDICTIONS : "evaluates batch"

    PRODUCTS {
        int product_id PK
        string product_name
        string category
        string unit
        numeric purchase_price
        numeric selling_price
        int shelf_life_days
        timestamp created_at
    }

    SUPPLIERS {
        int supplier_id PK
        string supplier_name
        string contact_person
        string phone
        string email
        text address
        int average_delivery_days
        int minimum_order_quantity
        boolean is_active
        timestamp created_at
    }

    INVENTORY {
        int inventory_id PK
        int product_id FK
        string batch_number
        int quantity
        date purchase_date
        date expiry_date
        numeric storage_temperature
        timestamp created_at
    }

    SALES {
        int sale_id PK
        int product_id FK
        int quantity_sold
        numeric selling_price
        date sale_date
        time sale_time
        timestamp created_at
    }

    PURCHASE_ORDERS {
        int purchase_order_id PK
        int supplier_id FK
        int product_id FK
        int quantity_ordered
        date order_date
        date expected_delivery_date
        string status
        numeric unit_cost
        timestamp created_at
    }

    WEATHER_DATA {
        int weather_id PK
        string location
        numeric temperature
        numeric humidity
        numeric rainfall
        date weather_date
        timestamp created_at
    }

    DEMAND_FORECASTS {
        int forecast_id PK
        int product_id FK
        date forecast_date
        numeric predicted_demand
        string model_name
        timestamp created_at
    }

    SPOILAGE_PREDICTIONS {
        int prediction_id PK
        int product_id FK
        int inventory_id FK
        date prediction_date
        int days_remaining
        numeric spoilage_probability
        string risk_level
        string model_name
        timestamp created_at
    }

    ANALYTICS {
        int analytics_id PK
        int product_id FK
        date analysis_date
        int total_sales
        numeric total_revenue
        int wastage_quantity
        numeric wastage_cost
        numeric stock_turnover
        timestamp created_at
    }

    USERS {
        int user_id PK
        string username UK
        string email UK
        string password_hash
        string role
        timestamp created_at
    }
```

---

## Key Cardinality Rationale

1. **`PRODUCTS` &rarr; `INVENTORY` (1 to Many):** A single perishable catalog product (e.g. "Milk") can have multiple batches (`MILK-B001`, `MILK-B002`) received on different days with distinct expiry dates and storage temperatures.
2. **`PRODUCTS` &rarr; `SALES` (1 to Many):** A product appears across multiple historical transaction events over time.
3. **`SUPPLIERS` &rarr; `PURCHASE_ORDERS` (1 to Many):** A supplier receives multiple replenishment purchase orders.
4. **`PRODUCTS` &rarr; `DEMAND_FORECASTS` (1 to Many):** Demand is projected across different dates for each product.
5. **`INVENTORY` &rarr; `SPOILAGE_PREDICTIONS` (1 to Many):** Spoilage risk can be tracked per batch over time as days remaining decreases toward expiry.
