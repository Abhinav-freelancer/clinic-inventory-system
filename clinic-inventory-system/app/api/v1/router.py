"""
API router configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, items, usage, alerts, reports # type: ignore

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
