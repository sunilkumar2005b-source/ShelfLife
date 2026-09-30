-- ============================================================
-- ShelfLife: AI-Powered Perishable Inventory Management System
-- Database Initialization Script (PostgreSQL)
-- Database Name: shelflife_db
-- ============================================================

-- Ensure clean schema if re-creating
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- ------------------------------------------------------------
-- 1. PRODUCTS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit VARCHAR(20),
    purchase_price NUMERIC(10, 2) DEFAULT 0.00,
    selling_price NUMERIC(10, 2) DEFAULT 0.00,
    shelf_life_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_products_selling_price CHECK (selling_price >= 0),
    CONSTRAINT chk_products_purchase_price CHECK (purchase_price >= 0),
    CONSTRAINT chk_products_shelf_life CHECK (shelf_life_days > 0)
);

-- ------------------------------------------------------------
-- 2. SUPPLIERS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    average_delivery_days INT DEFAULT 2,
    minimum_order_quantity INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_supplier_delivery_days CHECK (average_delivery_days >= 0),
    CONSTRAINT chk_supplier_min_order CHECK (minimum_order_quantity >= 1)
);

-- ------------------------------------------------------------
-- 3. INVENTORY TABLE (Batches of Perishables)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    batch_number VARCHAR(50),
    quantity INT NOT NULL DEFAULT 0,
    purchase_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE NOT NULL,
    storage_temperature NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_inventory_quantity CHECK (quantity >= 0)
);

-- ------------------------------------------------------------
-- 4. SALES TABLE (Point-of-Sale Transactions)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_sold INT NOT NULL,
    selling_price NUMERIC(10, 2) NOT NULL,
    sale_date DATE NOT NULL DEFAULT CURRENT_DATE,
    sale_time TIME DEFAULT CURRENT_TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_sales_quantity CHECK (quantity_sold > 0),
    CONSTRAINT chk_sales_price CHECK (selling_price >= 0)
);

-- ------------------------------------------------------------
-- 5. PURCHASE ORDERS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_orders (
    purchase_order_id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_ordered INT NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_delivery_date DATE,
    status VARCHAR(30) DEFAULT 'Pending',
    unit_cost NUMERIC(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_po_quantity CHECK (quantity_ordered > 0),
    CONSTRAINT chk_po_unit_cost CHECK (unit_cost >= 0)
);

-- ------------------------------------------------------------
-- 6. WEATHER DATA TABLE (Environmental Conditions)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_data (
    weather_id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    temperature NUMERIC(5, 2),
    humidity NUMERIC(5, 2),
    rainfall NUMERIC(6, 2) DEFAULT 0.00,
    weather_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 7. DEMAND FORECASTS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_demand NUMERIC(10, 2) NOT NULL,
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_forecast_demand CHECK (predicted_demand >= 0)
);

-- ------------------------------------------------------------
-- 8. SPOILAGE PREDICTIONS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spoilage_predictions (
    prediction_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    inventory_id INT REFERENCES inventory(inventory_id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    days_remaining INT,
    spoilage_probability NUMERIC(4, 2),
    risk_level VARCHAR(20),
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_spoilage_prob CHECK (spoilage_probability >= 0.0 AND spoilage_probability <= 1.0),
    CONSTRAINT chk_spoilage_days_remaining CHECK (days_remaining >= 0)
);

-- ------------------------------------------------------------
-- 9. ANALYTICS TABLE (Aggregated KPIs)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics (
    analytics_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_sales INT DEFAULT 0,
    total_revenue NUMERIC(12, 2) DEFAULT 0.00,
    wastage_quantity INT DEFAULT 0,
    wastage_cost NUMERIC(12, 2) DEFAULT 0.00,
    stock_turnover NUMERIC(8, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 10. USERS TABLE (Authentication / Authorization)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'store_owner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PERFORMANCE & LOOKUP INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry_date ON inventory(expiry_date);
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier_id ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_product_id ON purchase_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_demand_forecasts_prod_date ON demand_forecasts(product_id, forecast_date DESC);
CREATE INDEX IF NOT EXISTS idx_spoilage_predictions_prod_inv ON spoilage_predictions(product_id, inventory_id);
CREATE INDEX IF NOT EXISTS idx_weather_data_date ON weather_data(weather_date);
