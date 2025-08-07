"""
Pydantic schemas for item management
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ItemBase(BaseModel):
    name: str
    type: str
    stock_quantity: int = 0
    unit: str
    expiry_date: Optional[date] = None
    reorder_threshold: int = 10
    daily_usage_rate: float = 0.0
    barcode: Optional[str] = None
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    reorder_threshold: Optional[int] = None
    daily_usage_rate: Optional[float] = None
    barcode: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    is_active: bool
    last_updated: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ItemFilter(BaseModel):
    type: Optional[str] = None
    low_stock: Optional[bool] = None
    expiring_soon: Optional[bool] = None
    search: Optional[str] = None
