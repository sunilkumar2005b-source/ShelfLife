import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

from database import get_db_cursor
from services.ml_service import sync_database_predictions

def clean_database():
    with get_db_cursor(commit=True) as cur:
        # 1. Remove spoilage predictions for the 3 test batches
        cur.execute("DELETE FROM spoilage_predictions WHERE inventory_id IN (28, 29, 30);")
        print("Deleted test spoilage predictions for batches 28, 29, 30")
        
        # 2. Delete test batches
        cur.execute("DELETE FROM inventory WHERE inventory_id IN (28, 29, 30);")
        print("Deleted test batches 28, 29, 30 from inventory")
        
        # 3. Rename API Test Butter to Butter and cheese to Cheese
        cur.execute("UPDATE products SET product_name = 'Butter' WHERE product_id = 16;")
        cur.execute("UPDATE products SET product_name = 'Cheese' WHERE product_id = 25;")
        print("Renamed product 16 to Butter, product 25 to Cheese")

    # 4. Resync ML predictions
    res = sync_database_predictions()
    print("ML predictions resynced:", res.message)

    # 5. Verify current state
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT p.product_id, p.product_name, p.unit,
                   COALESCE(SUM(i.quantity), 0) as total_qty,
                   COUNT(i.inventory_id) as batch_count
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id, p.product_name, p.unit
            ORDER BY p.product_id;
        """)
        print("\n--- UPDATED PRODUCT STOCKS ---")
        for row in cur.fetchall():
            print(f"Product #{row[0]}: {row[1]:<12} | {row[3]:>3} {row[2]:<8} | {row[4]} batches")

if __name__ == "__main__":
    clean_database()
