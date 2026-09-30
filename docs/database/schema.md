# ShelfLife Database Schema Specification

## Database Details
- **DBMS:** PostgreSQL 18.x
- **Database Name:** `shelflife_db`
- **Host / Port:** `localhost:5432`
- **Driver:** `psycopg2-binary` (Python 3.13)

---

## 1. Relational Entities Specification

### 1.1 `products`
Catalog of perishable items available in the retail store.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `product_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique product identifier |
| `product_name` | `VARCHAR(100)` | `NO` | | Name of the perishable item |
| `category` | `VARCHAR(50)` | `YES` | | Category (Dairy, Bakery, Fruit, Vegetable) |
| `unit` | `VARCHAR(20)` | `YES` | | Unit of measurement (kg, litre, packet, piece) |
| `purchase_price` | `NUMERIC(10,2)`| `YES` | `CHECK (purchase_price >= 0)` | Cost to acquire from supplier |
| `selling_price` | `NUMERIC(10,2)`| `YES` | `CHECK (selling_price >= 0)` | Retail sale price |
| `shelf_life_days`| `INT` | `NO` | `CHECK (shelf_life_days > 0)` | Expected fresh shelf life in days |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

---

### 1.2 `suppliers`
Wholesale vendors and distributors supplying perishables.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `supplier_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique supplier identifier |
| `supplier_name` | `VARCHAR(100)` | `NO` | | Name of vendor or supplier business |
| `contact_person`| `VARCHAR(100)` | `YES` | | Primary contact representative |
| `phone` | `VARCHAR(20)` | `YES` | | Contact telephone number |
| `email` | `VARCHAR(100)` | `YES` | | Supplier email address |
| `address` | `TEXT` | `YES` | | Warehouse or business address |
| `average_delivery_days`| `INT` | `YES` | `DEFAULT 2, CHECK (>= 0)` | Vendor lead time in days |
| `minimum_order_quantity`| `INT` | `YES` | `DEFAULT 1, CHECK (>= 1)` | Minimum order size per purchase order |
| `is_active` | `BOOLEAN` | `YES` | `DEFAULT TRUE` | Supplier operational status |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

---

### 1.3 `inventory`
Physical batches of perishable goods on retail store shelves or storage.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `inventory_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique batch inventory identifier |
| `product_id` | `INT` | `NO` | `REFERENCES products(product_id)` | Foreign key to product catalog |
| `batch_number` | `VARCHAR(50)` | `YES` | | Traceable batch or lot code |
| `quantity` | `INT` | `NO` | `DEFAULT 0, CHECK (quantity >= 0)` | Number of physical units in stock |
| `purchase_date` | `DATE` | `YES` | `DEFAULT CURRENT_DATE` | Date batch was received/purchased |
| `expiry_date` | `DATE` | `NO` | | Manufacturer or estimated expiry date |
| `storage_temperature`| `NUMERIC(5,2)`| `YES` | | Storage temperature in Celsius |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_inventory_product_id` on `(product_id)`, `idx_inventory_expiry_date` on `(expiry_date)`.

---

### 1.4 `sales`
Point-of-sale customer checkout transactions.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `sale_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique sale transaction identifier |
| `product_id` | `INT` | `NO` | `REFERENCES products(product_id)` | Item sold |
| `quantity_sold` | `INT` | `NO` | `CHECK (quantity_sold > 0)` | Quantity purchased by customer |
| `selling_price` | `NUMERIC(10,2)`| `NO` | `CHECK (selling_price >= 0)` | Price charged per unit |
| `sale_date` | `DATE` | `NO` | `DEFAULT CURRENT_DATE` | Date transaction occurred |
| `sale_time` | `TIME` | `YES` | `DEFAULT CURRENT_TIME` | Time transaction occurred |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_sales_product_id` on `(product_id)`, `idx_sales_sale_date` on `(sale_date)`.

---

### 1.5 `purchase_orders`
Restock orders placed with suppliers.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `purchase_order_id`| `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique purchase order ID |
| `supplier_id` | `INT` | `NO` | `REFERENCES suppliers(supplier_id)` | Supplier fulfilling order |
| `product_id` | `INT` | `NO` | `REFERENCES products(product_id)` | Product ordered |
| `quantity_ordered` | `INT` | `NO` | `CHECK (quantity_ordered > 0)` | Units ordered |
| `order_date` | `DATE` | `NO` | `DEFAULT CURRENT_DATE` | Date order placed |
| `expected_delivery_date`| `DATE` | `YES` | | Estimated arrival date |
| `status` | `VARCHAR(30)` | `YES` | `DEFAULT 'Pending'` | Order status ('Pending', 'Received', 'Cancelled') |
| `unit_cost` | `NUMERIC(10,2)`| `YES` | `CHECK (unit_cost >= 0)` | Cost agreed per unit |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_purchase_orders_supplier_id` on `(supplier_id)`, `idx_purchase_orders_product_id` on `(product_id)`.

---

### 1.6 `weather_data`
Local environmental observations influencing perishable demand and degradation rates.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `weather_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique weather observation ID |
| `location` | `VARCHAR(100)` | `NO` | | City / store location |
| `temperature` | `NUMERIC(5,2)` | `YES` | | Ambient outdoor temperature (°C) |
| `humidity` | `NUMERIC(5,2)` | `YES` | | Relative humidity percentage (%) |
| `rainfall` | `NUMERIC(6,2)` | `YES` | `DEFAULT 0.00` | Rainfall in millimetres (mm) |
| `weather_date` | `DATE` | `NO` | | Date of weather record |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_weather_data_date` on `(weather_date)`.

---

### 1.7 `demand_forecasts`
Expected consumer demand predictions for products.

> [!NOTE]
> Entries in this table are **Synthetic Demo Records** until Section 7 model training is performed.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `forecast_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique forecast record ID |
| `product_id` | `INT` | `NO` | `REFERENCES products(product_id)` | Forecasted item |
| `forecast_date`| `DATE` | `NO` | | Target date for demand projection |
| `predicted_demand`| `NUMERIC(10,2)`| `NO` | `CHECK (predicted_demand >= 0)`| Estimated sales volume (units) |
| `model_name` | `VARCHAR(100)` | `YES` | | Model name (e.g., 'Random Forest (Demo Seed)') |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_demand_forecasts_prod_date` on `(product_id, forecast_date DESC)`.

---

### 1.8 `spoilage_predictions`
Calculated spoilage probabilities and risk tier classifications for inventory batches.

> [!NOTE]
> Entries in this table are **Synthetic Demo Records** until Section 7 model training is performed.

| Column | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `prediction_id` | `SERIAL` (INT) | `NO` | `PRIMARY KEY` | Unique prediction record ID |
| `product_id` | `INT` | `NO` | `REFERENCES products(product_id)` | Product evaluated |
| `inventory_id` | `INT` | `YES` | `REFERENCES inventory(inventory_id)` | Specific batch evaluated |
| `prediction_date`| `DATE` | `NO` | `DEFAULT CURRENT_DATE` | Date prediction was computed |
| `days_remaining`| `INT` | `YES` | `CHECK (days_remaining >= 0)` | Days remaining until batch expiration |
| `spoilage_probability`| `NUMERIC(4,2)`| `YES` | `CHECK (between 0.0 and 1.0)` | Probability of spoilage [0.00 - 1.00] |
| `risk_level` | `VARCHAR(20)` | `YES` | | Categorical risk ('Low', 'Medium', 'High') |
| `model_name` | `VARCHAR(100)` | `YES` | | Model identifier |
| `created_at` | `TIMESTAMP` | `YES` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

*Index:* `idx_spoilage_predictions_prod_inv` on `(product_id, inventory_id)`.

---

## 2. Integrity and Optimization Summary

1. **Foreign Key Enforcement**: All child tables (`inventory`, `sales`, `purchase_orders`, `demand_forecasts`, `spoilage_predictions`) enforce referential integrity back to parent tables.
2. **Domain Check Constraints**: Enforced at the engine level to prevent invalid data states (negative prices, negative inventory, out-of-bounds probabilities).
3. **Analytical Indexes**: 9 dedicated btree indexes support high-speed relational joins and time-series sorting for inventory intelligence queries.
