from typing import Optional
from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    supplier_name: str = Field(..., min_length=1, max_length=100, description="Supplier business name")
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    average_delivery_days: int = Field(2, ge=0)
    minimum_order_quantity: int = Field(1, ge=1)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    supplier_id: int

    class Config:
        from_attributes = True
