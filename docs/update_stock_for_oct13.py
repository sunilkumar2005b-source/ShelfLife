import sys
from pathlib import Path
from datetime import date, timedelta

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

from database import get_db_cursor
from services.ml_service import sync_database_predictions

def refresh_products_and_inventory():
    print("Connecting to PostgreSQL to fully refresh products and inventory for Oct 13, 2026...")
    today = date(2026, 10, 13)

    # 1. Standardize and capitalize product catalog names
    with get_db_cursor(commit=True) as cur:
        cur.execute("UPDATE products SET product_name = 'Carrot' WHERE product_id = 26;")
        cur.execute("UPDATE products SET product_name = 'Onion' WHERE product_id = 27;")
        cur.execute("UPDATE products SET product_name = 'Cheese' WHERE product_id = 25;")
        cur.execute("UPDATE products SET product_name = 'Butter' WHERE product_id = 16;")
        print("[OK] Product names standardized.")

        # 2. Insert standard ambient weather observation for today (24.5C, 55% humidity)
        cur.execute("""
            INSERT INTO weather_data (location, temperature, humidity, rainfall, weather_date)
            VALUES ('Main Retail Store', 24.5, 55.0, 0.0, %s);
        """, (today,))
        print(f"[OK] Normal baseline weather recorded for {today}.")

        # 3. Configure all 15 inventory batches relative to TODAY (2026-10-13)
        # Distribution:
        # - Urgent (1-2 days left): CAKE-B001 (1d), MILK-B002 (2d), PAN-B001 (2d)
        # - Expiring Soon (3-5 days left): BREAD-B001 (3d), TOM-B001 (4d), BAN-B001 (4d), CURD-B001 (5d), CAKE-B002 (5d)
        # - Good Shelf Life (>5 days left): MILK-B001 (7d), CARR-B001 (7d), ONIO-B001 (8d), ORG-B001 (7d), CHS-B001 (11d), BUT-B001 (14d), APP-B001 (22d)
        batch_configs = [
            # Urgent (<=2 days)
            {
                "id": 8, "batch": "CAKE-B001", "qty": 15,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=1),   # 2026-10-14 (1 day left -> Urgent Clearance)
                "temp": 16.0
            },
            {
                "id": 16, "batch": "MILK-B002", "qty": 20,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=2),   # 2026-10-15 (2 days left -> Urgent Clearance / FEFO 1st)
                "temp": 4.0
            },
            {
                "id": 6, "batch": "PAN-B001", "qty": 22,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=2),   # 2026-10-15 (2 days left -> Sell Quickly)
                "temp": 4.0
            },

            # Expiring Soon (3 - 5 days)
            {
                "id": 2, "batch": "BREAD-B001", "qty": 30,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=3),   # 2026-10-16 (3 days left)
                "temp": 20.0
            },
            {
                "id": 3, "batch": "TOM-B001", "qty": 35,
                "purch": today - timedelta(days=1), # 2026-10-12
                "exp": today + timedelta(days=4),   # 2026-10-17 (4 days left)
                "temp": 12.0
            },
            {
                "id": 4, "batch": "BAN-B001", "qty": 31,
                "purch": today - timedelta(days=1), # 2026-10-12
                "exp": today + timedelta(days=4),   # 2026-10-17 (4 days left)
                "temp": 15.0
            },
            {
                "id": 5, "batch": "CURD-B001", "qty": 25,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=5),   # 2026-10-18 (5 days left)
                "temp": 4.0
            },
            {
                "id": 21, "batch": "CAKE-B002", "qty": 20,
                "purch": today,                     # 2026-10-13
                "exp": today + timedelta(days=5),   # 2026-10-18 (5 days left -> FEFO 2nd batch)
                "temp": 16.0
            },

            # Good Shelf Life (>5 days)
            {
                "id": 1, "batch": "MILK-B001", "qty": 45,
                "purch": today,                     # 2026-10-13
                "exp": today + timedelta(days=7),   # 2026-10-20 (7 days left -> FEFO 2nd batch)
                "temp": 4.0
            },
            {
                "id": 31, "batch": "CARR-B001", "qty": 20,
                "purch": today - timedelta(days=1), # 2026-10-12
                "exp": today + timedelta(days=7),   # 2026-10-20 (7 days left)
                "temp": 10.0
            },
            {
                "id": 32, "batch": "ONIO-B001", "qty": 25,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=8),   # 2026-10-21 (8 days left)
                "temp": 18.0
            },
            {
                "id": 25, "batch": "ORG-B001", "qty": 25,
                "purch": today - timedelta(days=1), # 2026-10-12
                "exp": today + timedelta(days=7),   # 2026-10-20 (7 days left)
                "temp": 10.0
            },
            {
                "id": 26, "batch": "CHS-B001", "qty": 20,
                "purch": today - timedelta(days=1), # 2026-10-12
                "exp": today + timedelta(days=11),  # 2026-10-24 (11 days left)
                "temp": 4.0
            },
            {
                "id": 27, "batch": "BUT-B001", "qty": 25,
                "purch": today - timedelta(days=2), # 2026-10-11
                "exp": today + timedelta(days=14),  # 2026-10-27 (14 days left)
                "temp": 4.0
            },
            {
                "id": 7, "batch": "APP-B001", "qty": 40,
                "purch": today - timedelta(days=4), # 2026-10-09
                "exp": today + timedelta(days=22),  # 2026-11-04 (22 days left)
                "temp": 8.0
            },
        ]

        for b in batch_configs:
            cur.execute("""
                UPDATE inventory
                SET quantity = %s,
                    purchase_date = %s,
                    expiry_date = %s,
                    storage_temperature = %s
                WHERE inventory_id = %s;
            """, (b["qty"], b["purch"], b["exp"], b["temp"], b["id"]))
            print(f"  -> Updated Batch ID {b['id']:2d} ({b['batch']:10s}): Qty={b['qty']:2d}, Exp={b['exp']}")

    print("\n[OK] All 15 inventory batches calibrated with fresh shelf-life dates.")
    print("Synchronizing ML Demand Forecasts and Spoilage Risk Predictions...")
    sync_res = sync_database_predictions()
    print(f"[OK] ML sync completed: {sync_res.message}")

    # Verify and print summary
    print("\n==================== VERIFIED INVENTORY FOR OCT 13, 2026 ====================")
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT 
                i.batch_number,
                p.product_name,
                p.category,
                i.quantity,
                p.unit,
                i.purchase_date,
                i.expiry_date,
                (i.expiry_date - CURRENT_DATE) AS days_left,
                sp.spoilage_probability,
                sp.risk_level
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            LEFT JOIN (
                SELECT DISTINCT ON (inventory_id) inventory_id, spoilage_probability, risk_level
                FROM spoilage_predictions
                ORDER BY inventory_id, prediction_id DESC
            ) sp ON i.inventory_id = sp.inventory_id
            ORDER BY i.expiry_date ASC, i.inventory_id ASC;
        """)
        rows = cur.fetchall()
        print(f"{'BATCH':<12} {'PRODUCT':<12} {'CATEGORY':<10} {'QTY':<8} {'PURCHASE':<12} {'EXPIRY':<12} {'DAYS':<6} {'SPOILAGE':<10} {'RISK'}")
        print("-" * 92)
        for r in rows:
            qty_str = f"{r[3]} {r[4]}"
            spoil_pct = f"{float(r[8])*100:.1f}%" if r[8] is not None else "N/A"
            risk = str(r[9]) if r[9] is not None else "N/A"
            print(f"{r[0]:<12} {r[1]:<12} {r[2]:<10} {qty_str:<8} {str(r[5]):<12} {str(r[6]):<12} {str(r[7])+'d':<6} {spoil_pct:<10} {risk}")

if __name__ == "__main__":
    refresh_products_and_inventory()
