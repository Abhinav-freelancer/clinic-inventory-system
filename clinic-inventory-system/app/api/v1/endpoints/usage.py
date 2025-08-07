from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class UsageRecord(BaseModel):
    item_id: int
    quantity_used: int
    used_by: str
    notes: str = None

@router.get("/", response_model=List[dict])
async def get_usage_records():
    """Get all usage records"""
    return [{"id": 1, "item_id": 1, "quantity_used": 5, "used_by": "Dr. Smith"}]

@router.post("/", response_model=dict)
async def create_usage_record(record: UsageRecord):
    """Create new usage record"""
    return {"id": 2, "item_id": record.item_id, "quantity_used": record.quantity_used, "used_by": record.used_by}

@router.get("/{record_id}")
async def get_usage_record(record_id: int):
    """Get specific usage record"""
    return {"id": record_id, "item_id": 1, "quantity_used": 5, "used_by": "Dr. Smith"}
