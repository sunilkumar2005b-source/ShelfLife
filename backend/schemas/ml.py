"""
Pydantic Schemas for Machine Learning Endpoints
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DemandPredictionRequest(BaseModel):
    product_id: Optional[int] = Field(None, description="Optional ID of existing product in database")
    category: Optional[str] = Field("Fruits & Vegetables", description="Product category")
    stock_quantity: Optional[int] = Field(50, ge=0, description="Current shelf quantity")
    reorder_level: Optional[int] = Field(30, ge=0, description="Reorder threshold")
    reorder_quantity: Optional[int] = Field(20, ge=0, description="Replenishment batch size")
    unit_price: Optional[float] = Field(4.50, ge=0.0, description="Unit price")
    shelf_life_days: Optional[int] = Field(14, ge=1, description="Rated shelf life in days")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month of demand (1-12)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")


class DemandPredictionResponse(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    category: str
    predicted_demand: float
    model_name: str
    input_features: Dict[str, Any]


class SpoilagePredictionRequest(BaseModel):
    inventory_id: Optional[int] = Field(None, description="Optional ID of existing inventory batch")
    product_id: Optional[int] = Field(None, description="Product ID")
    category: Optional[str] = Field("Dairy", description="Product category")
    stock_quantity: Optional[int] = Field(40, ge=0, description="Current batch quantity")
    days_remaining: Optional[int] = Field(3, ge=0, description="Days remaining until expiry")
    unit_price: Optional[float] = Field(3.50, ge=0.0, description="Unit price")
    sales_volume: Optional[float] = Field(50.0, ge=0.0, description="Monthly sales velocity")
    turnover_rate: Optional[float] = Field(45.0, ge=0.0, description="Inventory turnover rate")
    total_shelf_life: Optional[int] = Field(14, ge=1, description="Total rated shelf life")


class SpoilagePredictionResult(BaseModel):
    inventory_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    risk_level: str
    spoilage_probability: float
    class_probabilities: Dict[str, float]
    model_name: str


class MLSyncResponse(BaseModel):
    success: bool
    synced_demand_forecasts: int
    synced_spoilage_predictions: int
    message: str


class MLStatusResponse(BaseModel):
    status: str
    demand_model: Dict[str, Any]
    spoilage_model: Dict[str, Any]
