"""
ShelfLife Advanced Analytics & Financial Waste Service (Section 9)
Provides store-level financial waste valuation, capital-at-risk calculations,
waste reduction discount simulations, and exportable inventory audit formatting.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from database import get_db_cursor
from services.intelligence_service import (
    calculate_health_score,
    health_status,
    get_recommendation,
)


def get_financial_risk_summary() -> Dict[str, Any]:
    """
    Computes comprehensive store-level financial valuation and perishable capital-at-risk.
    """
    with get_db_cursor() as cur:
        # Fetch joined inventory batches with product purchase/selling prices and latest ML spoilage predictions
        cur.execute("""
            SELECT
                i.inventory_id,
                p.product_id,
                p.product_name,
                p.category,
                i.quantity,
                COALESCE(p.purchase_price, 0.0) AS purchase_price,
                COALESCE(p.selling_price, 0.0) AS selling_price,
                COALESCE(sp.spoilage_probability, 0.5) AS spoilage_prob,
                COALESCE(sp.risk_level, 'Medium') AS risk_level,
                GREATEST(0, (i.expiry_date - CURRENT_DATE)) AS days_remaining
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            LEFT JOIN (
                SELECT DISTINCT ON (inventory_id)
                    inventory_id, spoilage_probability, risk_level
                FROM spoilage_predictions
                ORDER BY inventory_id, prediction_id DESC
            ) sp ON i.inventory_id = sp.inventory_id
            ORDER BY i.inventory_id
        """)
        rows = cur.fetchall()

        total_units = 0
        total_cost_valuation = 0.0
        total_retail_valuation = 0.0

        high_risk_cost = 0.0
        medium_risk_cost = 0.0
        low_risk_cost = 0.0

        high_risk_retail = 0.0
        projected_lost_margin = 0.0

        category_breakdown = {}

        for row in rows:
            qty = int(row[4])
            cost_price = float(row[5])
            sell_price = float(row[6])
            prob = float(row[7])
            risk = str(row[8]).capitalize()
            cat = str(row[3])

            batch_cost = round(qty * cost_price, 2)
            batch_retail = round(qty * sell_price, 2)
            margin = round(batch_retail - batch_cost, 2)

            total_units += qty
            total_cost_valuation += batch_cost
            total_retail_valuation += batch_retail

            if risk == "High":
                high_risk_cost += batch_cost
                high_risk_retail += batch_retail
                projected_lost_margin += margin
            elif risk == "Medium":
                medium_risk_cost += batch_cost
            else:
                low_risk_cost += batch_cost

            if cat not in category_breakdown:
                category_breakdown[cat] = {
                    "total_cost": 0.0,
                    "total_units": 0,
                    "high_risk_cost": 0.0,
                }
            category_breakdown[cat]["total_cost"] += batch_cost
            category_breakdown[cat]["total_units"] += qty
            if risk == "High":
                category_breakdown[cat]["high_risk_cost"] += batch_cost

        # Calculate category percentages
        category_stats = []
        for cat, val in category_breakdown.items():
            pct = round((val["high_risk_cost"] / val["total_cost"] * 100), 1) if val["total_cost"] > 0 else 0.0
            category_stats.append({
                "category": cat,
                "total_valuation": round(val["total_cost"], 2),
                "high_risk_valuation": round(val["high_risk_cost"], 2),
                "risk_percentage": pct,
                "total_units": val["total_units"],
            })

        category_stats.sort(key=lambda x: x["high_risk_valuation"], reverse=True)

        capital_at_risk_pct = round((high_risk_cost / total_cost_valuation * 100), 1) if total_cost_valuation > 0 else 0.0

        return {
            "total_inventory_units": total_units,
            "total_inventory_cost_valuation": round(total_cost_valuation, 2),
            "total_retail_potential_revenue": round(total_retail_valuation, 2),
            "capital_at_high_risk": round(high_risk_cost, 2),
            "capital_at_medium_risk": round(medium_risk_cost, 2),
            "capital_safe_low_risk": round(low_risk_cost, 2),
            "capital_at_risk_percentage": capital_at_risk_pct,
            "projected_lost_retail_margin": round(projected_lost_margin, 2),
            "category_risk_breakdown": category_stats,
        }


def simulate_clearance_discount(discount_percent: float = 30.0) -> Dict[str, Any]:
    """
    Simulates financial recovery if store applies a promotional clearance discount (e.g. 30%)
    on high spoilage risk perishable batches instead of allowing total loss.
    """
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT
                i.inventory_id,
                p.product_name,
                p.category,
                i.quantity,
                p.purchase_price,
                p.selling_price,
                COALESCE(sp.risk_level, 'Medium') AS risk_level
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            LEFT JOIN (
                SELECT DISTINCT ON (inventory_id)
                    inventory_id, risk_level
                FROM spoilage_predictions
                ORDER BY inventory_id, prediction_id DESC
            ) sp ON i.inventory_id = sp.inventory_id
            WHERE sp.risk_level = 'High'
        """)
        high_risk_items = cur.fetchall()

        total_cost_at_risk = 0.0
        discounted_revenue_recovered = 0.0
        original_retail_value = 0.0

        items_affected = []

        discount_multiplier = (100.0 - discount_percent) / 100.0

        for item in high_risk_items:
            qty = int(item[3])
            cost = float(item[4])
            retail = float(item[5])

            batch_cost = qty * cost
            batch_retail = qty * retail
            discounted_revenue = batch_retail * discount_multiplier

            total_cost_at_risk += batch_cost
            original_retail_value += batch_retail
            discounted_revenue_recovered += discounted_revenue

            items_affected.append({
                "inventory_id": item[0],
                "product_name": item[1],
                "category": item[2],
                "quantity": qty,
                "original_price": retail,
                "discounted_price": round(retail * discount_multiplier, 2),
                "recovered_revenue": round(discounted_revenue, 2),
                "avoided_loss": round(batch_cost, 2),
            })

        net_capital_saved = discounted_revenue_recovered
        savings_over_total_loss = discounted_revenue_recovered

        return {
            "discount_percentage_applied": discount_percent,
            "total_items_simulated": len(items_affected),
            "unmitigated_cost_loss": round(total_cost_at_risk, 2),
            "original_retail_value": round(original_retail_value, 2),
            "estimated_discounted_revenue_recovered": round(discounted_revenue_recovered, 2),
            "net_capital_salvaged": round(net_capital_saved, 2),
            "simulated_items": items_affected,
        }


def apply_demo_scenario(scenario: str) -> Dict[str, Any]:
    """
    Applies live preset business scenarios for faculty evaluations:
    - 'normal': Balanced baseline inventory and standard 24°C temperature
    - 'heatwave': Severe ambient heatwave (41°C, 88% humidity) accelerating perishable spoilage
    - 'urgent_clearance': Multiple perishable batches set to expire tomorrow, forcing clearance
    - 'stockout_crisis': Depleted stock on high-demand perishables, forcing urgent replenishment
    """
    with get_db_cursor(commit=True) as cur:
        if scenario == "heatwave":
            # Insert extreme heatwave weather observation
            cur.execute("""
                INSERT INTO weather_data (location, temperature, humidity, rainfall, weather_date)
                VALUES ('Main Retail Store', 41.5, 88.0, 0.0, CURRENT_DATE);
            """)
            # Slightly elevate storage temperatures in non-refrigerated batches
            cur.execute("""
                UPDATE inventory
                SET storage_temperature = 12.0
                WHERE storage_temperature IS NOT NULL AND storage_temperature < 10.0;
            """)
            msg = "Heatwave scenario applied: Ambient temperature raised to 41.5°C with 88% humidity. Storage temperatures elevated."

        elif scenario == "urgent_clearance":
            # Set Dairy and Bakery items to expire in 1 day
            cur.execute("""
                UPDATE inventory
                SET expiry_date = CURRENT_DATE + INTERVAL '1 day'
                WHERE inventory_id IN (1, 2, 3, 5, 8);
            """)
            msg = "Urgent Clearance scenario applied: Batches 1, 2, 3, 5, and 8 expiration forced to 1 day remaining."

        elif scenario == "stockout_crisis":
            # Set high-demand products to critically low stock (2 units)
            cur.execute("""
                UPDATE inventory
                SET quantity = 2
                WHERE product_id IN (1, 3, 4);
            """)
            msg = "Stockout Crisis scenario applied: Milk, Tomato, and Banana inventory reduced to 2 units against high demand."

        else: # "normal" or "reset"
            # Baseline temperatures
            cur.execute("""
                INSERT INTO weather_data (location, temperature, humidity, rainfall, weather_date)
                VALUES ('Main Retail Store', 24.0, 55.0, 0.0, CURRENT_DATE);
            """)
            # Reset staggered expiry dates
            cur.execute("""
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '4 days', quantity = 25, storage_temperature = 4.0 WHERE inventory_id = 1;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '7 days', quantity = 20, storage_temperature = 18.0 WHERE inventory_id = 2;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '5 days', quantity = 25, storage_temperature = 12.0 WHERE inventory_id = 3;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '8 days', quantity = 30, storage_temperature = 16.0 WHERE inventory_id = 4;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '4 days', quantity = 15, storage_temperature = 4.0 WHERE inventory_id = 5;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '6 days', quantity = 12, storage_temperature = 4.0 WHERE inventory_id = 6;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '90 days', quantity = 20, storage_temperature = 22.0 WHERE inventory_id = 7;
                UPDATE inventory SET expiry_date = CURRENT_DATE + INTERVAL '3 days', quantity = 10, storage_temperature = 18.0 WHERE inventory_id = 8;
            """)
            msg = "Baseline normal operation restored. Balanced inventory stock, standard temperatures, and staggered shelf lives active."

    # Automatically re-sync predictions to reflect the new scenario state
    from services.ml_service import sync_database_predictions
    sync_res = sync_database_predictions()

    return {
        "success": True,
        "scenario_applied": scenario,
        "message": msg,
        "sync_details": sync_res.model_dump(),
    }
