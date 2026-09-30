from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Product sold ID")
    quantity_sold: int = Field(..., gt=0, description="Units sold")
    selling_price: Optional[float] = Field(None, ge=0, description="Price charged per unit. Defaults to catalog price if omitted.")
    sale_date: Optional[date] = Field(None, description="Date of sale. Defaults to CURRENT_DATE.")
    sale_time: Optional[time] = Field(None, description="Time of sale. Defaults to CURRENT_TIME.")


class SaleResponse(BaseModel):
    sale_id: int
    product_id: int
    product_name: str
    category: Optional[str] = None
    quantity_sold: int
    selling_price: float
    sale_date: str
    sale_time: Optional[str] = None

    class Config:
        from_attributes = True
