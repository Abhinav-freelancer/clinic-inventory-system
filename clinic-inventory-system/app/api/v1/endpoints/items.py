from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    quantity: int
    category: str
    description: str = None

class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    category: str
    description: str = None

@router.get("/", response_model=List[dict])
async def get_items():
    """Get all items"""
    return [{"id": 1, "name": "Sample Item", "quantity": 10, "category": "Medical"}]

@router.post("/", response_model=dict)
async def create_item(item: ItemCreate):
    """Create new item"""
    return {"id": 2, "name": item.name, "quantity": item.quantity, "category": item.category}

@router.get("/{item_id}")
async def get_item(item_id: int):
    """Get specific item"""
    return {"id": item_id, "name": "Sample Item", "quantity": 10}

@router.put("/{item_id}")
async def update_item(item_id: int, item: ItemCreate):
    """Update item"""
    return {"id": item_id, "name": item.name, "quantity": item.quantity, "category": item.category}

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """Delete item"""
    return {"message": f"Item {item_id} deleted successfully"}
