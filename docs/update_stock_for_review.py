"""
Update inventory stocks, purchase dates, and expiry dates for the Review-2 demo (07.10.2026).
Ensures healthy stock on hand, clear FEFO multi-batch hierarchies, and properly calibrated
Urgent (<=2d), Expiring Soon (3-5d), and Good Shelf Life (>5d) batches.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

from database import get_db_cursor
from services.ml_service import sync_database_predictions

def update_inventory_for_review():
    print("Connecting to PostgreSQL to update inventory for Review-2...")

    # Base reference date: October 6, 2026 (Tomorrow is Review Day: 2026-10-07)
    today = date(2026, 10, 6)

    # Clean batch updates
    # Tomorrow (2026-10-07):
    # - CAKE-B001: Expiry 2026-10-08 (1 day left -> Urgent Clearance)
    # - MILK-B002: Expiry 2026-10-09 (2 days left -> Urgent Clearance / Sell Quickly)
    # - BREAD-B001: Expiry 2026-10-10 (3 days left -> Expiring Soon)
    # - TOM-B001: Expiry 2026-10-11 (4 days left -> Expiring Soon)
    # - PAN-B001: Expiry 2026-10-11 (4 days left -> Expiring Soon)
    # - CURD-B001: Expiry 2026-10-11 (4 days left -> Expiring Soon)
    # - CAKE-B002: Expiry 2026-10-12 (5 days left -> Expiring Soon / Second Batch)
    # - BAN-B001: Expiry 2026-10-12 (5 days left -> Expiring Soon)
    # - MILK-B001: Expiry 2026-10-14 (7 days left -> Good Shelf Life / Second Batch)
    # - APP-B001: Expiry 2026-10-28 (21 days left -> Good Shelf Life)

    updates = [
        # Cake: 2 batches (15 + 20 = 35 total)
        {
            "id": 8, "batch": "CAKE-B001", "qty": 15,
            "purch": today - timedelta(days=2), # 2026-10-04
            "exp": today + timedelta(days=2),   # 2026-10-08 (1 day left tomorrow)
            "temp": 16.0
        },
        {
            "id": 21, "batch": "CAKE-B002", "qty": 20,
            "purch": today,                     # 2026-10-06
            "exp": today + timedelta(days=6),   # 2026-10-12 (5 days left tomorrow)
            "temp": 16.0
        },

        # Milk: 2 batches (20 + 45 = 65 total)
        {
            "id": 16, "batch": "MILK-B002", "qty": 20,
            "purch": today - timedelta(days=2), # 2026-10-04
            "exp": today + timedelta(days=3),   # 2026-10-09 (2 days left tomorrow)
            "temp": 4.0
        },
        {
            "id": 1, "batch": "MILK-B001", "qty": 45,
            "purch": today,                     # 2026-10-06
            "exp": today + timedelta(days=8),   # 2026-10-14 (7 days left tomorrow)
            "temp": 4.0
        },

        # Bread (Bakery): 30 units
        {
            "id": 2, "batch": "BREAD-B001", "qty": 30,
            "purch": today - timedelta(days=2), # 2026-10-04
            "exp": today + timedelta(days=4),   # 2026-10-10 (3 days left tomorrow)
            "temp": 20.0
        },

        # Tomato (Vegetable): 35 units
        {
            "id": 3, "batch": "TOM-B001", "qty": 35,
            "purch": today - timedelta(days=1), # 2026-10-05
            "exp": today + timedelta(days=5),   # 2026-10-11 (4 days left tomorrow)
            "temp": 12.0
        },

        # Paneer (Dairy): 22 units
        {
            "id": 6, "batch": "PAN-B001", "qty": 22,
            "purch": today - timedelta(days=1), # 2026-10-05
            "exp": today + timedelta(days=5),   # 2026-10-11 (4 days left tomorrow)
            "temp": 4.0
        },

        # Curd (Dairy): 25 units
        {
            "id": 5, "batch": "CURD-B001", "qty": 25,
            "purch": today - timedelta(days=2), # 2026-10-04
            "exp": today + timedelta(days=5),   # 2026-10-11 (4 days left tomorrow)
            "temp": 4.0
        },

        # Banana (Fruit): 32 units
        {
            "id": 4, "batch": "BAN-B001", "qty": 32,
            "purch": today - timedelta(days=1), # 2026-10-05
            "exp": today + timedelta(days=6),   # 2026-10-12 (5 days left tomorrow)
            "temp": 15.0
        },

        # Apple (Fruit): 40 units
        {
            "id": 7, "batch": "APP-B001", "qty": 40,
            "purch": today - timedelta(days=4), # 2026-10-02
            "exp": today + timedelta(days=22),  # 2026-10-28 (21 days left tomorrow)
            "temp": 8.0
        },
    ]

    with get_db_cursor(commit=True) as cur:
        for u in updates:
            cur.execute("""
                UPDATE inventory
                SET quantity = %s,
                    purchase_date = %s,
                    expiry_date = %s,
                    storage_temperature = %s
                WHERE inventory_id = %s;
            """, (u["qty"], u["purch"], u["exp"], u["temp"], u["id"]))
            print(f"Updated Batch ID {u['id']:2d} ({u['batch']:10s}): Qty={u['qty']:2d}, Purch={u['purch']}, Exp={u['exp']}")

        # Ensure Orange batch exists for Product ID 21 if it has product record
        cur.execute("SELECT product_id FROM products WHERE product_id = 21;")
        if cur.fetchone():
            cur.execute("SELECT inventory_id FROM inventory WHERE product_id = 21;")
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO inventory (product_id, batch_number, quantity, purchase_date, expiry_date, storage_temperature)
                    VALUES (21, 'ORG-B001', 25, '2026-10-05', '2026-10-18', 10.0);
                """)
                print("Added Batch for Orange (ORG-B001): Qty=25, Exp=2026-10-18")

    print("\n[OK] Database inventory table updated successfully!")
    print("Now synchronizing ML Demand Forecasts and Spoilage Risk Predictions...")
    sync_res = sync_database_predictions()
    print(f"[OK] ML Sync completed: {sync_res.message}")

    # Print summary of updated batches
    print("\n==================== UPDATED INVENTORY FOR REVIEW-2 ====================")
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT 
                i.batch_number,
                p.product_name,
                p.category,
                i.quantity,
                i.purchase_date,
                i.expiry_date,
                (i.expiry_date - CURRENT_DATE) AS days_left,
                sp.spoilage_probability,
                sp.risk_level
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            LEFT JOIN spoilage_predictions sp ON i.inventory_id = sp.inventory_id
            ORDER BY i.expiry_date ASC, i.inventory_id ASC;
        """)
        rows = cur.fetchall()
        print(f"{'BATCH':<12} {'PRODUCT':<12} {'CATEGORY':<10} {'QTY':<5} {'PURCHASE':<12} {'EXPIRY':<12} {'DAYS':<6} {'SPOILAGE':<10} {'RISK'}")
        print("-" * 88)
        for r in rows:
            spoil_pct = f"{float(r[7])*100:.1f}%" if r[7] is not None else "N/A"
            risk = str(r[8]) if r[8] is not None else "N/A"
            print(f"{r[0]:<12} {r[1]:<12} {r[2]:<10} {r[3]:<5} {str(r[4]):<12} {str(r[5]):<12} {str(r[6])+'d':<6} {spoil_pct:<10} {risk}")

if __name__ == "__main__":
    update_inventory_for_review()
