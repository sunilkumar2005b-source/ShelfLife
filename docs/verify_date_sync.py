import urllib.request
import json

with urllib.request.urlopen("http://localhost:5173/api/inventory") as r:
    inv = json.loads(r.read().decode())

with urllib.request.urlopen("http://localhost:5173/api/inventory-intelligence") as r:
    intel = json.loads(r.read().decode())

intel_map = {item["inventory_id"]: item for item in intel}

print("=" * 76)
print(f"{'BATCH':<12} {'PRODUCT':<10} {'EXPIRY':<12} {'INVENTORY':<12} {'AI ENGINE':<12} {'RECOMMENDATION'}")
print("=" * 76)

all_match = True
for b in sorted(inv, key=lambda x: x["expiry_date"]):
    iid = b["inventory_id"]
    it = intel_map.get(iid, {})
    batch = b.get("batch_number", "N/A")
    prod = b.get("product_name", "N/A")
    exp = b.get("expiry_date", "N/A")
    inv_days = b.get("days_remaining")
    intel_days = it.get("days_remaining")
    rec = it.get("recommendation", "N/A")

    match_str = "[OK]" if inv_days == intel_days else "[MISMATCH]"
    if inv_days != intel_days:
        all_match = False
    print(f"{batch:<12} {prod:<10} {exp:<12} {str(inv_days)+' days':<12} {str(intel_days)+' days':<12} {rec} {match_str}")

print("=" * 76)
if all_match:
    print("VERIFICATION PASSED: Every inventory batch and AI Decision Engine item has 100% identical days remaining!")
else:
    print("VERIFICATION FAILED: Discrepancy detected.")
