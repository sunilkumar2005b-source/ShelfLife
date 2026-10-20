from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Product foreign key ID")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch identifier")
    quantity: int = Field(0, ge=0, description="Quantity in inventory")
    purchase_date: Optional[date] = Field(None, description="Date batch received")
    expiry_date: date = Field(..., description="Date batch expires")
    storage_temperature: Optional[float] = Field(None, description="Storage temperature in Celsius")


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    batch_number: Optional[str] = Field(None, max_length=50)
    quantity: Optional[int] = Field(None, ge=0)
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    storage_temperature: Optional[float] = None


class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    product_name: str
    category: Optional[str] = None
    batch_number: Optional[str] = None
    quantity: int
    purchase_date: Optional[str] = None
    expiry_date: str
    storage_temperature: Optional[float] = None
    unit: Optional[str] = None
    days_remaining: Optional[int] = None

    class Config:
        from_attributes = True
