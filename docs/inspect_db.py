import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from database import get_db_cursor

with get_db_cursor() as cur:
    print("--- PRODUCTS ---")
    cur.execute("SELECT product_id, product_name, category, purchase_price, selling_price, shelf_life_days FROM products ORDER BY product_id;")
    for p in cur.fetchall():
        print(p)

    print("\n--- INVENTORY ---")
    cur.execute("""
        SELECT i.inventory_id, i.batch_number, p.product_name, p.category, i.quantity, i.purchase_date, i.expiry_date, i.storage_temperature
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        ORDER BY i.inventory_id;
    """)
    for row in cur.fetchall():
        print(row)
