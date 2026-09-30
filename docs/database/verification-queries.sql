-- ============================================================
-- ShelfLife: SQL Verification Queries
-- Use these queries in pgAdmin, psql, or via Python backend
-- to verify database integrity, counts, and relational linkages.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Core Entity Verification Queries
-- ------------------------------------------------------------

-- Check Products Table
SELECT * FROM products ORDER BY product_id;

-- Check Inventory Batches
SELECT * FROM inventory ORDER BY inventory_id;

-- Check Sales Transactions
SELECT * FROM sales ORDER BY sale_id;

-- Check Suppliers
SELECT * FROM suppliers ORDER BY supplier_id;

-- Check Purchase Orders
SELECT * FROM purchase_orders ORDER BY purchase_order_id;

-- Check Weather Observations
SELECT * FROM weather_data ORDER BY weather_date;

-- Check Demand Forecasts (Demo / Synthetic Data)
SELECT * FROM demand_forecasts ORDER BY forecast_id;

-- Check Spoilage Predictions (Demo / Synthetic Data)
SELECT * FROM spoilage_predictions ORDER BY prediction_id;

-- ------------------------------------------------------------
-- 2. Relational Linkage and JOIN Verification
-- ------------------------------------------------------------

-- Verify Product -> Inventory Relationship
SELECT 
    i.inventory_id,
    p.product_id,
    p.product_name,
    p.category,
    i.batch_number,
    i.quantity,
    i.expiry_date,
    (i.expiry_date - CURRENT_DATE) AS days_to_expiry
FROM inventory i
JOIN products p ON i.product_id = p.product_id
ORDER BY i.expiry_date ASC;

-- Verify Product -> Sales Relationship
SELECT 
    s.sale_id,
    p.product_name,
    s.quantity_sold,
    s.selling_price,
    (s.quantity_sold * s.selling_price) AS transaction_revenue,
    s.sale_date,
    s.sale_time
FROM sales s
JOIN products p ON s.product_id = p.product_id
ORDER BY s.sale_date DESC, s.sale_time DESC;

-- Verify Supplier -> Purchase Orders -> Products
SELECT 
    po.purchase_order_id,
    s.supplier_name,
    p.product_name,
    po.quantity_ordered,
    po.unit_cost,
    (po.quantity_ordered * po.unit_cost) AS total_order_cost,
    po.status,
    po.order_date,
    po.expected_delivery_date
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id
JOIN products p ON po.product_id = p.product_id
ORDER BY po.order_date DESC;

-- Verify Inventory -> Spoilage Prediction Linkage
SELECT 
    sp.prediction_id,
    p.product_name,
    i.batch_number,
    i.quantity AS current_stock,
    sp.days_remaining,
    sp.spoilage_probability,
    sp.risk_level,
    sp.model_name
FROM spoilage_predictions sp
JOIN products p ON sp.product_id = p.product_id
JOIN inventory i ON sp.inventory_id = i.inventory_id
ORDER BY sp.spoilage_probability DESC;

-- Verify Product -> Demand Forecast Linkage
SELECT 
    df.forecast_id,
    p.product_name,
    df.forecast_date,
    df.predicted_demand,
    df.model_name
FROM demand_forecasts df
JOIN products p ON df.product_id = p.product_id
ORDER BY df.forecast_date DESC;

-- ------------------------------------------------------------
-- 3. Composite Inventory Intelligence View
-- ------------------------------------------------------------
SELECT 
    i.inventory_id,
    p.product_name,
    i.quantity AS stock,
    df.predicted_demand,
    sp.spoilage_probability,
    sp.risk_level,
    (i.expiry_date - CURRENT_DATE) AS days_remaining
FROM inventory i
JOIN products p ON i.product_id = p.product_id
LEFT JOIN LATERAL (
    SELECT predicted_demand 
    FROM demand_forecasts df 
    WHERE df.product_id = i.product_id 
    ORDER BY df.forecast_date DESC 
    LIMIT 1
) df ON TRUE
LEFT JOIN LATERAL (
    SELECT spoilage_probability, risk_level 
    FROM spoilage_predictions sp 
    WHERE sp.product_id = i.product_id AND sp.inventory_id = i.inventory_id 
    ORDER BY sp.prediction_date DESC 
    LIMIT 1
) sp ON TRUE
ORDER BY i.inventory_id;
