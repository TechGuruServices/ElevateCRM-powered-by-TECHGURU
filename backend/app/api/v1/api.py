"""
TECHGURU ElevateCRM API Router v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    users,
    contacts,
    products,
    orders,
    dashboard,
    integrations,
    inventory,
    websocket,
    search
)
from app.api.v1 import auth, dev

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/v1", tags=["authentication"])
api_router.include_router(dev.router, prefix="/v1", tags=["development"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/v1/contacts", tags=["contacts"])
api_router.include_router(products.router, prefix="/v1/products", tags=["products"])
api_router.include_router(orders.router, prefix="/v1/orders", tags=["orders"])
api_router.include_router(dashboard.router, prefix="/v1/dashboard", tags=["dashboard"])
api_router.include_router(integrations.router, prefix="/v1/integrations", tags=["integrations"])
api_router.include_router(inventory.router, prefix="/v1/inventory", tags=["inventory"])
api_router.include_router(websocket.router, prefix="/v1/realtime", tags=["websocket", "realtime"])
api_router.include_router(search.router, prefix="/v1/search", tags=["search"])