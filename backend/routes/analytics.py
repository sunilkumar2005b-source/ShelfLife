from typing import List
from fastapi import APIRouter, HTTPException, status
from database import get_db_cursor
from schemas.intelligence import (
    DemandForecastResponse,
    SpoilagePredictionResponse,
    DashboardSummaryResponse,
    InventoryIntelligenceItem,
    InventoryIntelligenceSummaryResponse,
)
from services.rule_config import RuleConfig, get_rule_config, update_rule_config
from services.intelligence_service import (
    days_until_expiry,
    calculate_health_score,
    health_status,
    get_recommendation,
    get_spoilage_risk,
)

router = APIRouter(tags=["Analytics & Intelligence"])


@router.get("/demand-forecasts", response_model=List[DemandForecastResponse])
def get_demand_forecasts():
    """
    Retrieve demand forecasts for products.
    NOTE: Records currently sourced from seeded demonstration data.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    df.forecast_id,
                    df.product_id,
                    p.product_name,
                    p.category,
                    df.forecast_date,
                    df.predicted_demand,
                    df.model_name
                FROM demand_forecasts df
                JOIN products p
                    ON df.product_id = p.product_id
                ORDER BY df.forecast_id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "forecast_id": r[0],
                    "product_id": r[1],
                    "product_name": r[2],
                    "category": r[3],
                    "forecast_date": str(r[4]),
                    "predicted_demand": float(r[5]),
                    "model_name": r[6]
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load demand forecasts: {str(error)}"
        )


@router.get("/spoilage-predictions", response_model=List[SpoilagePredictionResponse])
def get_spoilage_predictions():
    """
    Retrieve spoilage predictions for inventory batches.
    NOTE: Records currently sourced from seeded demonstration data.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    sp.prediction_id,
                    sp.product_id,
                    p.product_name,
                    p.category,
                    sp.inventory_id,
                    sp.prediction_date,
                    sp.days_remaining,
                    sp.spoilage_probability,
                    sp.risk_level,
                    sp.model_name
                FROM spoilage_predictions sp
                JOIN products p
                    ON sp.product_id = p.product_id
                ORDER BY sp.prediction_id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "prediction_id": r[0],
                    "product_id": r[1],
                    "product_name": r[2],
                    "category": r[3],
                    "inventory_id": r[4],
                    "prediction_date": str(r[5]),
                    "days_remaining": int(r[6]) if r[6] is not None else 0,
                    "spoilage_probability": float(r[7]) if r[7] is not None else 0.0,
                    "risk_level": r[8],
                    "model_name": r[9]
                }
                for r in rows
            ]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load spoilage predictions: {str(error)}"
        )


@router.get("/dashboard-summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary():
    """
    Provides aggregated metrics used by the executive dashboard cards.
    """
    try:
        with get_db_cursor() as cursor:
            # 1. Total products
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]

            # 2. Total inventory records
            cursor.execute("SELECT COUNT(*) FROM inventory")
            inventory_items = cursor.fetchone()[0]

            # 3. Spoilage risk distribution
            cursor.execute("""
                SELECT
                    LOWER(risk_level),
                    COUNT(*)
                FROM spoilage_predictions
                GROUP BY LOWER(risk_level)
            """)
            risk_rows = cursor.fetchall()

            high_risk = 0
            medium_risk = 0
            low_risk = 0
            for risk, count in risk_rows:
                if risk == "high":
                    high_risk = int(count)
                elif risk == "medium":
                    medium_risk = int(count)
                elif risk == "low":
                    low_risk = int(count)

            return {
                "total_products": total_products,
                "inventory_items": inventory_items,
                "high_spoilage_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "risk_summary": {
                    "high": high_risk,
                    "medium": medium_risk,
                    "low": low_risk
                }
            }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load dashboard summary: {str(error)}"
        )


# ============================================================
# RULE ENGINE CONFIGURATION ENDPOINTS (SECTION 5)
# ============================================================

@router.get("/inventory-intelligence/config", response_model=RuleConfig)
def get_intelligence_configuration():
    """
    Returns the active configurable parameters of the heuristic rule engine.
    Ensures zero magic numbers and full parameter transparency.
    """
    return get_rule_config()


@router.put("/inventory-intelligence/config", response_model=RuleConfig)
def update_intelligence_configuration(new_config: RuleConfig):
    """
    Update rule thresholds, weights, and environmental limits in real time.
    """
    return update_rule_config(new_config)


# ============================================================
# INVENTORY INTELLIGENCE SYNTHESIS
# ============================================================

@router.get("/inventory-intelligence", response_model=List[InventoryIntelligenceItem])
def get_inventory_intelligence():
    """
    Combines inventory batches, products, latest demand forecasts,
    spoilage predictions, storage conditions, and environmental weather data
    to calculate transparent health scores and actionable recommendations.
    """
    try:
        config = get_rule_config()

        with get_db_cursor() as cursor:
            # Fetch latest environmental weather observation
            cursor.execute("""
                SELECT temperature, humidity
                FROM weather_data
                ORDER BY weather_date DESC
                LIMIT 1
            """)
            weather_row = cursor.fetchone()
            ambient_temp = float(weather_row[0]) if weather_row and weather_row[0] is not None else None
            humidity = float(weather_row[1]) if weather_row and weather_row[1] is not None else None

            # Fetch joined inventory batches with product metadata, forecasts, and predictions
            cursor.execute("""
                SELECT
                    i.inventory_id,
                    i.product_id,
                    p.product_name,
                    p.category,
                    i.quantity,
                    i.expiry_date,
                    i.storage_temperature,
                    COALESCE(
                        (
                            SELECT df.predicted_demand
                            FROM demand_forecasts df
                            WHERE df.product_id = i.product_id
                            ORDER BY df.forecast_date DESC
                            LIMIT 1
                        ),
                        0
                    ) AS predicted_demand,
                    COALESCE(
                        (
                            SELECT sp.spoilage_probability
                            FROM spoilage_predictions sp
                            WHERE sp.product_id = i.product_id
                            AND sp.inventory_id = i.inventory_id
                            ORDER BY sp.prediction_date DESC
                            LIMIT 1
                        ),
                        0
                    ) AS spoilage_probability,
                    i.batch_number
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                ORDER BY i.inventory_id
            """)
            rows = cursor.fetchall()
            intelligence = []

            for row in rows:
                inventory_id = row[0]
                product_id = row[1]
                product_name = row[2]
                category = row[3]
                current_stock = float(row[4])
                expiry_date = row[5]
                storage_temp = float(row[6]) if row[6] is not None else None
                predicted_demand = float(row[7])
                spoilage_probability = float(row[8])
                batch_number = row[9]

                days_remaining = days_until_expiry(expiry_date)
                risk_level = get_spoilage_risk(spoilage_probability, config=config)

                score = calculate_health_score(
                    current_stock=current_stock,
                    predicted_demand=predicted_demand,
                    days_remaining=days_remaining,
                    spoilage_probability=spoilage_probability,
                    storage_temp=storage_temp,
                    category=category,
                    config=config
                )
                status_label = health_status(score)

                recommendation, explanation = get_recommendation(
                    current_stock=current_stock,
                    predicted_demand=predicted_demand,
                    days_remaining=days_remaining,
                    spoilage_probability=spoilage_probability,
                    storage_temp=storage_temp,
                    category=category,
                    ambient_temp=ambient_temp,
                    humidity=humidity,
                    config=config
                )

                intelligence.append({
                    "inventory_id": inventory_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "batch_number": batch_number,
                    "current_stock": int(current_stock),
                    "predicted_demand": int(predicted_demand),
                    "expiry_date": str(expiry_date),
                    "days_remaining": days_remaining,
                    "spoilage_probability": round(spoilage_probability, 2),
                    "spoilage_probability_percent": round(spoilage_probability * 100, 1),
                    "risk_level": risk_level,
                    "health_score": score,
                    "health_status": status_label,
                    "recommendation": recommendation,
                    "ai_explanation": explanation
                })

            return intelligence
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate inventory intelligence: {str(error)}"
        )


@router.get("/inventory-intelligence-summary", response_model=InventoryIntelligenceSummaryResponse)
def get_inventory_intelligence_summary():
    """
    Summarizes counts for each recommendation category.
    """
    try:
        data = get_inventory_intelligence()
        urgent_clearance = 0
        sell_quickly = 0
        reorder = 0
        monitor = 0
        sufficient = 0

        for item in data:
            rec = item["recommendation"]
            if rec in ("Clearance Action", "Urgent Clearance"):
                urgent_clearance += 1
            elif rec == "Sell Quickly":
                sell_quickly += 1
            elif rec == "Reorder":
                reorder += 1
            elif rec in ("Monitor", "Monitor Stock"):
                monitor += 1
            elif rec == "Sufficient Stock":
                sufficient += 1

        return {
            "urgent_clearance": urgent_clearance,
            "sell_quickly": sell_quickly,
            "reorder": reorder,
            "monitor": monitor,
            "sufficient": sufficient,
            "total": len(data)
        }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate intelligence summary: {str(error)}"
        )
