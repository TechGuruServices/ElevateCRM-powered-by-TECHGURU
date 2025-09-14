"""
TECHGURU ElevateCRM Models

Import all models to ensure they are registered with SQLAlchemy
"""
from app.models.company import Company
from app.models.user import User
from app.models.contact import Contact
from app.models.product import Product, StockLocation, StockMove
from app.models.order import Order, OrderLineItem
from app.models.integration import Integration, Webhook

__all__ = [
    "Company",
    "User", 
    "Contact",
    "Product",
    "StockLocation", 
    "StockMove",
    "Order",
    "OrderLineItem",
    "Integration",
    "Webhook"
]
