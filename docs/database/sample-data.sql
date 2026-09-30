-- ============================================================
-- ShelfLife: Demo / Synthetic Data Seed Script
-- WARNING: All records in this script are Demo / Synthetic Data
-- designed for system demonstration, UI testing, and API verification.
-- None of these entries represent real-world customer or sensor logs.
-- ============================================================

-- 1. Insert Products (Perishables)
INSERT INTO products (product_id, product_name, category, unit, purchase_price, selling_price, shelf_life_days)
VALUES
(1, 'Milk', 'Dairy', 'litre', 45.00, 55.00, 5),
(2, 'Bread', 'Bakery', 'packet', 30.00, 40.00, 7),
(3, 'Tomato', 'Vegetable', 'kg', 35.00, 50.00, 5),
(4, 'Banana', 'Fruit', 'dozen', 45.00, 60.00, 6),
(5, 'Curd', 'Dairy', 'cup', 25.00, 35.00, 7),
(6, 'Paneer', 'Dairy', 'gram', 70.00, 90.00, 5),
(7, 'Apple', 'Fruit', 'kg', 120.00, 160.00, 15),
(8, 'Cake', 'Bakery', 'piece', 150.00, 200.00, 3)
ON CONFLICT (product_id) DO NOTHING;

-- 2. Insert Suppliers
INSERT INTO suppliers (supplier_id, supplier_name, contact_person, phone, email, address, average_delivery_days, minimum_order_quantity)
VALUES
(1, 'Fresh Dairy Suppliers', 'Ravi Kumar', '9876543210', 'ravi@freshdairy.com', '12 Milk Colony, Chennai', 2, 10),
(2, 'Daily Bakery Foods', 'Arun Kumar', '9876543211', 'arun@dailybakery.com', '45 Oven Lane, Chennai', 2, 5),
(3, 'Green Fresh Vegetables', 'Suresh Kumar', '9876543212', 'suresh@greenfresh.com', '78 Farm Road, Chennai', 1, 15),
(4, 'Fruit World Suppliers', 'Vijay Kumar', '9876543213', 'vijay@fruitworld.com', '90 Orchard Ave, Chennai', 2, 10)
ON CONFLICT (supplier_id) DO NOTHING;

-- 3. Insert Inventory Batches
INSERT INTO inventory (inventory_id, product_id, batch_number, quantity, purchase_date, expiry_date, storage_temperature)
VALUES
(1, 1, 'MILK-B001', 30, '2026-09-14', '2026-09-19', 4.00),
(2, 2, 'BREAD-B001', 20, '2026-09-14', '2026-09-21', 25.00),
(3, 3, 'TOM-B001', 25, '2026-09-14', '2026-09-19', 22.00),
(4, 4, 'BAN-B001', 30, '2026-09-14', '2026-09-22', 23.00),
(5, 5, 'CURD-B001', 15, '2026-09-14', '2026-09-21', 4.00),
(6, 6, 'PAN-B001', 12, '2026-09-15', '2026-09-20', 4.00),
(7, 7, 'APP-B001', 20, '2026-09-12', '2026-09-28', 5.00),
(8, 8, 'CAKE-B001', 10, '2026-09-15', '2026-09-18', 5.00)
ON CONFLICT (inventory_id) DO NOTHING;

-- 4. Insert Sales Transactions
INSERT INTO sales (sale_id, product_id, quantity_sold, selling_price, sale_date, sale_time)
VALUES
(1, 1, 5, 55.00, '2026-08-17', '09:30:00'),
(2, 1, 4, 55.00, '2026-08-18', '11:15:00'),
(3, 2, 3, 40.00, '2026-08-17', '10:00:00'),
(4, 2, 5, 40.00, '2026-08-18', '16:45:00'),
(5, 3, 6, 50.00, '2026-08-18', '14:20:00'),
(6, 4, 8, 60.00, '2026-08-17', '12:10:00'),
(7, 5, 4, 35.00, '2026-08-18', '15:30:00'),
(8, 6, 3, 90.00, '2026-08-18', '17:00:00'),
(9, 7, 2, 160.00, '2026-08-18', '18:15:00'),
(10, 8, 2, 200.00, '2026-08-18', '19:00:00')
ON CONFLICT (sale_id) DO NOTHING;

-- 5. Insert Purchase Orders
INSERT INTO purchase_orders (purchase_order_id, supplier_id, product_id, quantity_ordered, order_date, expected_delivery_date, status, unit_cost)
VALUES
(1, 1, 1, 20, '2026-08-15', '2026-08-17', 'Received', 45.00),
(2, 1, 5, 10, '2026-08-15', '2026-08-17', 'Received', 25.00),
(3, 2, 2, 15, '2026-08-15', '2026-08-17', 'Received', 30.00),
(4, 2, 8, 8, '2026-08-16', '2026-08-18', 'Received', 150.00),
(5, 3, 3, 20, '2026-08-15', '2026-08-16', 'Received', 35.00),
(6, 4, 4, 25, '2026-08-15', '2026-08-17', 'Received', 45.00),
(7, 4, 7, 15, '2026-08-16', '2026-08-18', 'Pending', 120.00)
ON CONFLICT (purchase_order_id) DO NOTHING;

-- 6. Insert Weather Data
INSERT INTO weather_data (weather_id, location, temperature, humidity, rainfall, weather_date)
VALUES
(1, 'Chennai', 32.50, 72.00, 0.00, '2026-08-15'),
(2, 'Chennai', 33.00, 75.00, 2.50, '2026-08-16'),
(3, 'Chennai', 31.80, 78.00, 5.20, '2026-08-17'),
(4, 'Chennai', 32.20, 80.00, 1.00, '2026-08-18'),
(5, 'Chennai', 33.50, 76.00, 0.00, '2026-08-19')
ON CONFLICT (weather_id) DO NOTHING;

-- 7. Insert Demand Forecasts (LABEL: Demo / Synthetic Data)
INSERT INTO demand_forecasts (forecast_id, product_id, forecast_date, predicted_demand, model_name)
VALUES
(1, 1, '2026-08-20', 12.00, 'Random Forest (Demo Seed)'),
(2, 2, '2026-08-20', 8.00, 'Random Forest (Demo Seed)'),
(3, 3, '2026-08-20', 10.00, 'Random Forest (Demo Seed)'),
(4, 4, '2026-08-20', 14.00, 'Random Forest (Demo Seed)'),
(5, 5, '2026-08-20', 6.00, 'Random Forest (Demo Seed)'),
(6, 6, '2026-08-20', 5.00, 'Random Forest (Demo Seed)'),
(7, 7, '2026-08-20', 7.00, 'Random Forest (Demo Seed)'),
(8, 8, '2026-08-20', 4.00, 'Random Forest (Demo Seed)')
ON CONFLICT (forecast_id) DO NOTHING;

-- 8. Insert Spoilage Predictions (LABEL: Demo / Synthetic Data)
INSERT INTO spoilage_predictions (prediction_id, product_id, inventory_id, prediction_date, days_remaining, spoilage_probability, risk_level, model_name)
VALUES
(1, 1, 1, '2026-08-17', 3, 0.75, 'High', 'Random Forest (Demo Seed)'),
(2, 2, 2, '2026-08-17', 4, 0.45, 'Medium', 'Random Forest (Demo Seed)'),
(3, 3, 3, '2026-08-17', 3, 0.70, 'High', 'Random Forest (Demo Seed)'),
(4, 4, 4, '2026-08-17', 4, 0.55, 'Medium', 'Random Forest (Demo Seed)'),
(5, 5, 5, '2026-08-17', 4, 0.50, 'Medium', 'Random Forest (Demo Seed)'),
(6, 6, 6, '2026-08-17', 4, 0.40, 'Medium', 'Random Forest (Demo Seed)'),
(7, 7, 7, '2026-08-17', 10, 0.15, 'Low', 'Random Forest (Demo Seed)'),
(8, 8, 8, '2026-08-17', 2, 0.85, 'High', 'Random Forest (Demo Seed)')
ON CONFLICT (prediction_id) DO NOTHING;

-- Synchronize Sequences
SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products));
SELECT setval('suppliers_supplier_id_seq', (SELECT MAX(supplier_id) FROM suppliers));
SELECT setval('inventory_inventory_id_seq', (SELECT MAX(inventory_id) FROM inventory));
SELECT setval('sales_sale_id_seq', (SELECT MAX(sale_id) FROM sales));
SELECT setval('purchase_orders_purchase_order_id_seq', (SELECT MAX(purchase_order_id) FROM purchase_orders));
SELECT setval('weather_data_weather_id_seq', (SELECT MAX(weather_id) FROM weather_data));
SELECT setval('demand_forecasts_forecast_id_seq', (SELECT MAX(forecast_id) FROM demand_forecasts));
SELECT setval('spoilage_predictions_prediction_id_seq', (SELECT MAX(prediction_id) FROM spoilage_predictions));
