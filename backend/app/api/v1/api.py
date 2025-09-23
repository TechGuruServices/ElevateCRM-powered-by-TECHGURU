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
    search,
    notes,
    pricing,
    tasks
)
# Note: Requires pandas installation: pip install pandas>=2.2
from app.api.v1.endpoints import imports as imports_router
from app.api.v1.endpoints import orders as orders_router
from app.api.v1.endpoints import tasks as tasks_router
from app.api.v1.endpoints import notes as notes_router
from app.api.v1.endpoints import pricing as pricing_router
from app.api.v1 import auth, dev, ai_analytics


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/v1", tags=["authentication"])
api_router.include_router(dev.router, prefix="/v1", tags=["development"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/v1/contacts", tags=["contacts"])
api_router.include_router(products.router, prefix="/v1/products", tags=["products"])
api_router.include_router(orders_router.router, prefix="/v1/orders", tags=["orders"])
api_router.include_router(dashboard.router, prefix="/v1/dashboard", tags=["dashboard"])
api_router.include_router(integrations.router, prefix="/v1/integrations", tags=["integrations"])
api_router.include_router(inventory.router, prefix="/v1/inventory", tags=["inventory"])
api_router.include_router(websocket.router, prefix="/v1/realtime", tags=["websocket", "realtime"])
api_router.include_router(search.router, prefix="/v1/search", tags=["search"])
api_router.include_router(notes_router.router, prefix="/v1/notes", tags=["notes"])
api_router.include_router(pricing_router.router, prefix="/v1/pricing", tags=["pricing"])
api_router.include_router(tasks_router.router, prefix="/v1/tasks", tags=["tasks"])
api_router.include_router(timeline.router, prefix="/v1/timeline", tags=["timeline"])
api_router.include_router(import_wizard.router, prefix="/v1/import", tags=["import"])
# Note: Requires pandas installation: pip install pandas>=2.2
api_router.include_router(imports_router.router, prefix="/v1/imports", tags=["imports"])
api_router.include_router(ai_analytics.router, prefix="/v1/ai", tags=["ai", "analytics"])
