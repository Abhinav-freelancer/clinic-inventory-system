"""
Pydantic schemas for usage record management
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsageRecordBase(BaseModel):
    item_id: int
    quantity_used: float
    used_by: str
    patient_id: Optional[str] = None
    notes: Optional[str] = None

class UsageRecordCreate(UsageRecordBase):
    pass

class UsageRecordResponse(UsageRecordBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class UsageReport(BaseModel):
    item_name: str
    total_quantity_used: float
    usage_count: int
    average_daily_usage: float
