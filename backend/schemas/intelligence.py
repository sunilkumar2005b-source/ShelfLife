from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DemandForecastResponse(BaseModel):
    forecast_id: int
    product_id: int
    product_name: str
    category: Optional[str] = None
    forecast_date: str
    predicted_demand: float
    model_name: Optional[str] = None


class SpoilagePredictionResponse(BaseModel):
    prediction_id: int
    product_id: int
    product_name: str
    category: Optional[str] = None
    inventory_id: Optional[int] = None
    prediction_date: str
    days_remaining: int
    spoilage_probability: float
    risk_level: str
    model_name: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    total_products: int
    inventory_items: int
    high_spoilage_risk: int
    medium_risk: int
    low_risk: int
    risk_summary: Dict[str, int]


class InventoryIntelligenceItem(BaseModel):
    inventory_id: int
    product_id: int
    product_name: str
    category: Optional[str] = None
    batch_number: Optional[str] = None
    current_stock: int
    predicted_demand: int
    expiry_date: str
    days_remaining: int
    spoilage_probability: float
    spoilage_probability_percent: float
    risk_level: str
    health_score: int
    health_status: str
    recommendation: str
    ai_explanation: str


class InventoryIntelligenceSummaryResponse(BaseModel):
    urgent_clearance: int
    sell_quickly: int
    reorder: int
    monitor: int
    sufficient: int
    total: int
