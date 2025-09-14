"""
TECHGURU ElevateCRM Orders Endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def list_orders() -> Dict[str, Any]:
    """List orders for current tenant"""
    return {
        "orders": [],
        "total": 0,
        "limit": 10,
        "offset": 0
    }
