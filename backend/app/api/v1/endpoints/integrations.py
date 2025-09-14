"""
TECHGURU ElevateCRM Integrations Endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def list_integrations() -> Dict[str, Any]:
    """List available integrations"""
    return {
        "integrations": [
            {"id": "shopify", "name": "Shopify", "status": "available"},
            {"id": "quickbooks", "name": "QuickBooks", "status": "available"},
            {"id": "stripe", "name": "Stripe", "status": "available"}
        ]
    }
