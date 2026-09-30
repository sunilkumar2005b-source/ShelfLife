from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100, description="Product title")
    category: Optional[str] = Field(None, max_length=50, description="Category (Dairy, Bakery, Fruit, Vegetable)")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of measurement (kg, litre, packet, piece)")
    purchase_price: float = Field(0.0, ge=0, description="Purchase price per unit")
    selling_price: float = Field(0.0, ge=0, description="Retail selling price per unit")
    shelf_life_days: int = Field(..., gt=0, description="Nominal fresh shelf life in days")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=20)
    purchase_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    shelf_life_days: Optional[int] = Field(None, gt=0)


class ProductResponse(ProductBase):
    product_id: int

    class Config:
        from_attributes = True
