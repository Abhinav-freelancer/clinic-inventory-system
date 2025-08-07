from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class Alert(BaseModel):
    id: int
    type: str
    message: str
    item_id: int

@router.get("/", response_model=List[dict])
async def get_alerts():
    """Get all alerts"""
    return [{"id": 1, "type": "low_stock", "message": "Item running low", "item_id": 1}]

@router.post("/", response_model=dict)
async def create_alert():
    """Create new alert"""
    return {"id": 2, "type": "expiry", "message": "Item expiring soon", "item_id": 2}

@router.get("/{alert_id}")
async def get_alert(alert_id: int):
    """Get specific alert"""
    return {"id": alert_id, "type": "low_stock", "message": "Alert message", "item_id": 1}
