import urllib.request
import json

req = urllib.request.urlopen("http://127.0.0.1:8000/inventory")
data = json.loads(req.read().decode("utf-8"))
print(f"Total batches in DB: {len(data)}")
for b in data:
    print(f"ID: {b.get('inventory_id'):2d} | Batch: {b.get('batch_number'):10s} | Product: {b.get('product_name'):12s} | Qty: {b.get('quantity'):3d} | Purchase: {b.get('purchase_date')} | Expiry: {b.get('expiry_date')} | Days Left: {b.get('days_until_expiry')} | Temp: {b.get('storage_temperature')}")
