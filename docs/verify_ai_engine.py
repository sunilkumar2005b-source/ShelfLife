import urllib.request
import json

def verify_ai_engine():
    print("=" * 70)
    print("VERIFYING AI DECISION ENGINE & CLEARANCE MARKDOWN SIMULATOR")
    print("=" * 70)

    # 1. Test /inventory-intelligence
    req1 = urllib.request.Request('http://127.0.0.1:8000/inventory-intelligence')
    with urllib.request.urlopen(req1) as resp:
        intel = json.loads(resp.read().decode())
        print(f"\n1. Inventory Intelligence ({len(intel)} items evaluated):")
        for item in intel:
            print(f"   Batch #{item['inventory_id']:2d} | {item['product_name']:<10} | Days Left: {item['days_remaining']:2d}d | Health: {item['health_score']:2d}/100 ({item['health_status']:<15}) | Recommendation: {item['recommendation']}")

    # 2. Test /inventory-intelligence-summary
    req2 = urllib.request.Request('http://127.0.0.1:8000/inventory-intelligence-summary')
    with urllib.request.urlopen(req2) as resp:
        summary = json.loads(resp.read().decode())
        print(f"\n2. Recommendation Breakdown KPI Summary:")
        print(f"   - Urgent Clearance: {summary['urgent_clearance']}")
        print(f"   - Sell Quickly:     {summary['sell_quickly']}")
        print(f"   - Reorder Stock:    {summary['reorder']}")
        print(f"   - Monitor Stock:    {summary['monitor']}")
        print(f"   - Sufficient Stock: {summary['sufficient']}")
        print(f"   - Total Evaluated:  {summary['total']}")

    # 3. Test /reports/simulate-clearance (30% markdown discount)
    req3 = urllib.request.Request(
        'http://127.0.0.1:8000/reports/simulate-clearance',
        data=json.dumps({'discount_percent': 30.0}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req3) as resp:
        sim = json.loads(resp.read().decode())
        print(f"\n3. Clearance Markdown Simulator (at 30% markdown):")
        print(f"   - High-Risk Batches Rescued: {sim['total_items_simulated']}")
        print(f"   - Unmitigated Cost Loss:     Rs. {sim['unmitigated_cost_loss']:.2f}")
        print(f"   - Original Retail Value:     Rs. {sim['original_retail_value']:.2f}")
        print(f"   - Recovered Revenue:         Rs. {sim['estimated_discounted_revenue_recovered']:.2f}")
        print("   - Item Breakdown:")
        for it in sim['simulated_items']:
            print(f"     * {it['product_name']:<10} ({it['quantity']} units) | Regular: Rs. {it['original_price']:.2f} -> Markdown: Rs. {it['discounted_price']:.2f} | Salvaged: Rs. {it['recovered_revenue']:.2f}")

    # 4. Test /reports/financial-risk
    req4 = urllib.request.Request('http://127.0.0.1:8000/reports/financial-risk')
    with urllib.request.urlopen(req4) as resp:
        fin = json.loads(resp.read().decode())
        print(f"\n4. Store-Level Financial Risk Valuation:")
        print(f"   - Total Units on Hand:   {fin['total_inventory_units']}")
        print(f"   - Total Cost Valuation:  Rs. {fin['total_inventory_cost_valuation']:.2f}")
        print(f"   - Potential Retail Rev:  Rs. {fin['total_retail_potential_revenue']:.2f}")
        print(f"   - Capital at High Risk:  Rs. {fin['capital_at_high_risk']:.2f} ({fin['capital_at_risk_percentage']}%)")
        print(f"   - Capital at Medium Risk:Rs. {fin['capital_at_medium_risk']:.2f}")
        print(f"   - Safe Low-Risk Capital: Rs. {fin['capital_safe_low_risk']:.2f}")

if __name__ == "__main__":
    verify_ai_engine()
