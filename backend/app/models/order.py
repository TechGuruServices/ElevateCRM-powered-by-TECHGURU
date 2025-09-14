"""
TECHGURU ElevateCRM Order/Sales Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from sqlalchemy.orm import relationship

from app.core.database import Base


class Order(Base):
    """Order model for quotes, sales orders, purchase orders, invoices"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Order Identification
    order_number = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # quote, sales_order, purchase_order, invoice
    status = Column(String(50), default="draft")  # draft, sent, confirmed, fulfilled, cancelled
    
    # Customer/Contact Information
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)
    
    # Billing and Shipping
    billing_address = Column(JSON, nullable=True)
    shipping_address = Column(JSON, nullable=True)
    
    # Financial Information
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    currency = Column(String(10), default="USD")
    
    # Payment Information
    payment_terms = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), default="pending")  # pending, partial, paid, overdue
    
    # Important Dates
    order_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    shipped_date = Column(DateTime, nullable=True)
    delivered_date = Column(DateTime, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    properties = Column(JSON, default=dict)  # Custom fields
    
    # External References
    external_refs = Column(JSON, default=dict)  # Shopify order ID, QuickBooks invoice ID, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="orders")
    contact = relationship("Contact", back_populates="orders")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_orders")
    line_items = relationship("OrderLineItem", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def is_quote(self):
        """Check if order is a quote"""
        return self.type == "quote"
    
    @property
    def is_invoice(self):
        """Check if order is an invoice"""
        return self.type == "invoice"
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<Order {self.order_number} ({self.type})>"


class OrderLineItem(Base):
    """Order line item model"""
    __tablename__ = "order_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    
    # Item Information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(100), nullable=True)
    
    # Quantities and Pricing
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(15, 2), default=0)
    
    # Discounts and Taxes
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_percentage = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    
    # Additional Properties
    properties = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="line_items")
    product = relationship("Product", back_populates="order_line_items")
    
    def __repr__(self):
        return f"<OrderLineItem {self.name} x{self.quantity}>"
