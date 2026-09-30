from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(..., gt=0, description="Supplier identifier")
    product_id: int = Field(..., gt=0, description="Product identifier")
    quantity_ordered: int = Field(..., gt=0, description="Number of units ordered")
    order_date: Optional[date] = Field(None, description="Date ordered. Defaults to today.")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    status: Optional[str] = Field("Pending", description="Status (Pending, Received, Cancelled)")
    unit_cost: Optional[float] = Field(None, ge=0, description="Agreed unit cost. Defaults to product purchase price.")


class PurchaseOrderResponse(BaseModel):
    purchase_order_id: int
    supplier_id: int
    supplier_name: str
    product_id: int
    product_name: str
    quantity_ordered: int
    order_date: str
    expected_delivery_date: Optional[str] = None
    status: str
    unit_cost: float
    total_cost: float

    class Config:
        from_attributes = True
