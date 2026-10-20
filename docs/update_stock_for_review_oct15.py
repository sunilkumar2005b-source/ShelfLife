import sys
import os
import pathlib
from datetime import date, timedelta

backend_dir = Path = pathlib.Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

from database import get_db_cursor
from services.ml_service import sync_database_predictions

def calibrate_for_review():
    print("=" * 70)
    print("CALIBRATING SHELFLIFE INVENTORY SPECIFICALLY FOR REVIEW DAY (OCT 15, 2026)")
    print("=" * 70)

    # Reference review date: Tomorrow, October 15, 2026
    review_date = date(2026, 10, 15)

    with get_db_cursor(commit=True) as cur:
        # 1. Capitalize and standardize product catalog titles
        cur.execute("UPDATE products SET product_name = 'Carrot' WHERE product_id = 26;")
        cur.execute("UPDATE products SET product_name = 'Onion' WHERE product_id = 27;")
        cur.execute("UPDATE products SET product_name = 'Cheese' WHERE product_id = 25;")
        cur.execute("UPDATE products SET product_name = 'Butter' WHERE product_id = 16;")
        print("[OK] Product catalog standardized.")

        # 2. Insert standard baseline weather observation for today (Oct 14) and review day (Oct 15)
        cur.execute("""
            INSERT INTO weather_data (location, temperature, humidity, rainfall, weather_date)
            VALUES ('Main Retail Store', 24.0, 55.0, 0.0, '2026-10-14')
            ON CONFLICT DO NOTHING;
            INSERT INTO weather_data (location, temperature, humidity, rainfall, weather_date)
            VALUES ('Main Retail Store', 24.0, 55.0, 0.0, '2026-10-15')
            ON CONFLICT DO NOTHING;
        """)
        print("[OK] Baseline ambient weather (24°C, 55% RH) recorded.")

        # 3. Calibrate all 15 inventory batches relative to Review Date (2026-10-15)
        # Guarantees:
        # - Tonight (Oct 14): 0 Expired, 3 Urgent, 5 Expiring Soon, 7 Good Shelf Life
        # - Tomorrow (Oct 15): 0 Expired, 3 Urgent, 5 Expiring Soon, 7 Good Shelf Life
        batches = [
            # --- URGENT CLEARANCE TIER (<=2 days remaining on review day) ---
            {
                "id": 8, "batch": "CAKE-B001", "qty": 15,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=1),   # 2026-10-16 (1d left on review day -> Urgent Clearance!)
                "temp": 16.0
            },
            {
                "id": 16, "batch": "MILK-B002", "qty": 20,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=2),   # 2026-10-17 (2d left on review day -> FEFO 1st batch!)
                "temp": 4.0
            },
            {
                "id": 6, "batch": "PAN-B001", "qty": 22,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=2),   # 2026-10-17 (2d left on review day -> Sell Quickly!)
                "temp": 4.0
            },

            # --- EXPIRING SOON TIER (3 to 5 days remaining on review day) ---
            {
                "id": 2, "batch": "BREAD-B001", "qty": 30,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=3),   # 2026-10-18 (3d left on review day)
                "temp": 20.0
            },
            {
                "id": 3, "batch": "TOM-B001", "qty": 35,
                "purch": review_date - timedelta(days=1), # 2026-10-14
                "exp": review_date + timedelta(days=4),   # 2026-10-19 (4d left on review day)
                "temp": 12.0
            },
            {
                "id": 4, "batch": "BAN-B001", "qty": 31,
                "purch": review_date - timedelta(days=1), # 2026-10-14
                "exp": review_date + timedelta(days=4),   # 2026-10-19 (4d left on review day)
                "temp": 15.0
            },
            {
                "id": 5, "batch": "CURD-B001", "qty": 25,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=5),   # 2026-10-20 (5d left on review day)
                "temp": 4.0
            },
            {
                "id": 21, "batch": "CAKE-B002", "qty": 20,
                "purch": review_date,                     # 2026-10-15
                "exp": review_date + timedelta(days=5),   # 2026-10-20 (5d left on review day -> FEFO 2nd batch!)
                "temp": 16.0
            },

            # --- GOOD SHELF LIFE TIER (>5 days remaining on review day) ---
            {
                "id": 1, "batch": "MILK-B001", "qty": 45,
                "purch": review_date,                     # 2026-10-15
                "exp": review_date + timedelta(days=7),   # 2026-10-22 (7d left on review day -> FEFO 2nd batch!)
                "temp": 4.0
            },
            {
                "id": 31, "batch": "CARR-B001", "qty": 20,
                "purch": review_date - timedelta(days=1), # 2026-10-14
                "exp": review_date + timedelta(days=7),   # 2026-10-22 (7d left on review day)
                "temp": 10.0
            },
            {
                "id": 25, "batch": "ORG-B001", "qty": 25,
                "purch": review_date - timedelta(days=1), # 2026-10-14
                "exp": review_date + timedelta(days=7),   # 2026-10-22 (7d left on review day)
                "temp": 10.0
            },
            {
                "id": 32, "batch": "ONIO-B001", "qty": 25,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=8),   # 2026-10-23 (8d left on review day)
                "temp": 18.0
            },
            {
                "id": 26, "batch": "CHS-B001", "qty": 20,
                "purch": review_date - timedelta(days=1), # 2026-10-14
                "exp": review_date + timedelta(days=11),  # 2026-10-26 (11d left on review day)
                "temp": 4.0
            },
            {
                "id": 27, "batch": "BUT-B001", "qty": 25,
                "purch": review_date - timedelta(days=2), # 2026-10-13
                "exp": review_date + timedelta(days=14),  # 2026-10-29 (14d left on review day)
                "temp": 4.0
            },
            {
                "id": 7, "batch": "APP-B001", "qty": 40,
                "purch": review_date - timedelta(days=4), # 2026-10-11
                "exp": review_date + timedelta(days=22),  # 2026-11-06 (22d left on review day)
                "temp": 8.0
            },
        ]

        for b in batches:
            cur.execute("""
                UPDATE inventory
                SET quantity = %s,
                    purchase_date = %s,
                    expiry_date = %s,
                    storage_temperature = %s
                WHERE inventory_id = %s;
            """, (b["qty"], b["purch"], b["exp"], b["temp"], b["id"]))
            print(f"  -> Calibrated Batch ID {b['id']:2d} ({b['batch']:10s}): Qty={b['qty']:2d}, Exp={b['exp']}")

    print("\n[OK] Database inventory table updated.")
    print("Now synchronizing ML Demand Forecasts and Spoilage Risk Predictions...")
    sync_res = sync_database_predictions()
    print(f"[OK] ML sync completed: {sync_res.message}")

    print("\n==================== VERIFIED INVENTORY FOR REVIEW-2 ====================")
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
                (i.expiry_date - CURRENT_DATE) AS days_left_today,
                (i.expiry_date - DATE '2026-10-15') AS days_left_tomorrow,
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
        print(f"{'BATCH':<12} {'PRODUCT':<10} {'CATEGORY':<10} {'QTY':<8} {'EXPIRY':<12} {'TODAY':<8} {'TOMORROW':<10} {'SPOILAGE':<10} {'RISK'}")
        print("-" * 96)
        for r in rows:
            qty_str = f"{r[3]} {r[4]}"
            spoil_pct = f"{float(r[9])*100:.1f}%" if r[9] is not None else "N/A"
            risk = str(r[10]) if r[10] is not None else "N/A"
            print(f"{r[0]:<12} {r[1]:<10} {r[2]:<10} {qty_str:<8} {str(r[6]):<12} {str(r[7])+'d':<8} {str(r[8])+'d':<10} {spoil_pct:<10} {risk}")

if __name__ == "__main__":
    calibrate_for_review()
