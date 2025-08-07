from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class Report(BaseModel):
    id: int
    title: str
    data: dict

@router.get("/", response_model=List[dict])
async def get_reports():
    """Get all reports"""
    return [{"id": 1, "title": "Inventory Summary", "data": {"total_items": 100, "low_stock": 5}}]

@router.post("/", response_model=dict)
async def create_report():
    """Create new report"""
    return {"id": 2, "title": "Usage Report", "data": {"total_usage": 50, "top_item": "Bandages"}}

@router.get("/{report_id}")
async def get_report(report_id: int):
    """Get specific report"""
    return {"id": report_id, "title": "Report Title", "data": {"sample": "data"}}
