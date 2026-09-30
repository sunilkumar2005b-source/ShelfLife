"""
FastAPI Routes for Advanced Analytics, Report Exports, and Faculty Demo Scenarios (Section 9)
"""

import csv
import io
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from database import get_db_cursor
from services.analytics_service import (
    get_financial_risk_summary,
    simulate_clearance_discount,
    apply_demo_scenario,
)

router = APIRouter(tags=["Advanced Analytics & Reports"])


class DiscountSimulationRequest(BaseModel):
    discount_percent: float = Field(30.0, ge=5.0, le=90.0, description="Clearance markdown percentage")


class ScenarioRequest(BaseModel):
    scenario: str = Field(..., description="'normal', 'heatwave', 'urgent_clearance', or 'stockout_crisis'")


@router.get("/reports/financial-risk")
def get_financial_risk_endpoint():
    """
    Returns store-level valuation, capital-at-risk due to spoilage,
    projected lost retail margins, and category-by-category financial vulnerability.
    """
    try:
        return get_financial_risk_summary()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to compute financial risk summary: {str(error)}"
        )


@router.post("/reports/simulate-clearance")
def simulate_clearance_endpoint(req: DiscountSimulationRequest):
    """
    Simulates retail financial recovery from markdown discounts on high-risk batches.
    """
    try:
        return simulate_clearance_discount(req.discount_percent)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clearance markdown simulation failed: {str(error)}"
        )


@router.get("/reports/inventory-audit.csv")
def export_inventory_audit_csv():
    """
    Streams a complete, downloadable CSV inventory audit report with shelf life,
    storage conditions, health status, and action recommendations.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    i.inventory_id,
                    p.product_id,
                    p.product_name,
                    p.category,
                    i.batch_number,
                    i.quantity,
                    p.unit,
                    COALESCE(p.purchase_price, 0.0) AS cost_price,
                    COALESCE(p.selling_price, 0.0) AS retail_price,
                    i.purchase_date,
                    i.expiry_date,
                    GREATEST(0, (i.expiry_date - CURRENT_DATE)) AS days_remaining,
                    i.storage_temperature,
                    COALESCE(sp.spoilage_probability, 0.0) AS spoilage_prob,
                    COALESCE(sp.risk_level, 'Medium') AS risk_level,
                    COALESCE(df.predicted_demand, 0.0) AS predicted_demand
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                LEFT JOIN (
                    SELECT DISTINCT ON (inventory_id) inventory_id, spoilage_probability, risk_level
                    FROM spoilage_predictions
                    ORDER BY inventory_id, prediction_id DESC
                ) sp ON i.inventory_id = sp.inventory_id
                LEFT JOIN (
                    SELECT DISTINCT ON (product_id) product_id, predicted_demand
                    FROM demand_forecasts
                    ORDER BY product_id, forecast_id DESC
                ) df ON p.product_id = df.product_id
                ORDER BY i.inventory_id
            """)
            rows = cur.fetchall()

            output = io.StringIO()
            writer = csv.writer(output)

            # CSV Header
            writer.writerow([
                "Batch ID",
                "Product ID",
                "Product Name",
                "Category",
                "Batch Number",
                "Quantity On Hand",
                "Unit",
                "Cost Price ($)",
                "Total Cost Valuation ($)",
                "Selling Price ($)",
                "Potential Retail Revenue ($)",
                "Purchase Date",
                "Expiry Date",
                "Days Remaining",
                "Storage Temp (°C)",
                "Spoilage Probability (%)",
                "Risk Tier",
                "Forecasted Demand (Units)",
            ])

            for r in rows:
                qty = int(r[5])
                cost = float(r[7])
                retail = float(r[8])
                prob_pct = round(float(r[13]) * 100, 1)

                writer.writerow([
                    r[0], # inventory_id
                    r[1], # product_id
                    r[2], # product_name
                    r[3], # category
                    r[4], # batch_number
                    qty,
                    r[6], # unit
                    cost,
                    round(qty * cost, 2),
                    retail,
                    round(qty * retail, 2),
                    str(r[9]) if r[9] else "",
                    str(r[10]),
                    int(r[11]), # days_remaining
                    float(r[12]) if r[12] is not None else "N/A",
                    prob_pct,
                    r[14], # risk_level
                    float(r[15]), # predicted_demand
                ])

            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=shelflife_inventory_audit.csv"}
            )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to export inventory audit CSV: {str(error)}"
        )


@router.get("/reports/spoilage-risk.csv")
def export_spoilage_risk_csv():
    """
    Streams a downloadable CSV report focused exclusively on perishable degradation,
    days remaining, spoilage probabilities, and financial valuation at risk.
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    sp.prediction_id,
                    p.product_name,
                    p.category,
                    i.inventory_id,
                    i.batch_number,
                    i.quantity,
                    COALESCE(p.purchase_price, 0.0) AS cost_price,
                    sp.days_remaining,
                    sp.spoilage_probability,
                    sp.risk_level,
                    sp.model_name,
                    sp.prediction_date
                FROM spoilage_predictions sp
                JOIN products p ON sp.product_id = p.product_id
                JOIN inventory i ON sp.inventory_id = i.inventory_id
                ORDER BY sp.spoilage_probability DESC
            """)
            rows = cur.fetchall()

            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow([
                "Prediction ID",
                "Product Name",
                "Category",
                "Batch ID",
                "Batch Number",
                "Quantity",
                "Unit Cost ($)",
                "Capital At Risk ($)",
                "Days Remaining",
                "Spoilage Probability (%)",
                "Risk Tier",
                "Model Provenance",
                "Prediction Date",
            ])

            for r in rows:
                qty = int(r[5])
                cost = float(r[6])
                prob_pct = round(float(r[8]) * 100, 1)

                writer.writerow([
                    r[0], # prediction_id
                    r[1], # product_name
                    r[2], # category
                    r[3], # inventory_id
                    r[4], # batch_number
                    qty,
                    cost,
                    round(qty * cost, 2),
                    int(r[7]), # days_remaining
                    prob_pct,
                    r[9], # risk_level
                    r[10], # model_name
                    str(r[11]),
                ])

            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=shelflife_spoilage_risk.csv"}
            )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to export spoilage risk CSV: {str(error)}"
        )


@router.post("/demo/apply-scenario")
def apply_demo_scenario_endpoint(req: ScenarioRequest):
    """
    Applies live interactive scenarios for faculty evaluation:
    - 'normal': Baseline inventory & standard temperatures
    - 'heatwave': Severe ambient heatwave (41.5°C) accelerating perishable decay
    - 'urgent_clearance': Multiple batches expiring in 1 day forcing clearance
    - 'stockout_crisis': Depleted stock on high-demand perishables forcing replenishment
    """
    try:
        valid_scenarios = ["normal", "heatwave", "urgent_clearance", "stockout_crisis"]
        if req.scenario.lower() not in valid_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scenario '{req.scenario}'. Choose from {valid_scenarios}."
            )
        return apply_demo_scenario(req.scenario.lower())
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply scenario: {str(error)}"
        )
