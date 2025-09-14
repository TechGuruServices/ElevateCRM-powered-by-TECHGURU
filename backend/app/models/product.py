"""
TECHGURU ElevateCRM Product Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Product(Base):
    """Product/Service/SKU model"""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Product Type and Category
    type = Column(String(50), default="product")  # product, service, bundle, digital
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    
    # Pricing
    cost_price = Column(Numeric(10, 2), default=0)
    sale_price = Column(Numeric(10, 2), default=0)
    currency = Column(String(10), default="USD")
    
    # Physical Properties
    weight = Column(Numeric(10, 3), nullable=True)
    weight_unit = Column(String(10), default="kg")
    dimensions = Column(JSON, nullable=True)  # {length, width, height, unit}
    
    # Inventory Management
    track_inventory = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)
    
    # Status and Visibility
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    visibility = Column(String(20), default="public")  # public, private, archived
    
    # SEO and Media
    slug = Column(String(255), nullable=True, index=True)
    image_urls = Column(JSON, default=list)
    properties = Column(JSON, default=dict)  # Custom fields, variants, attributes
    
    # External References
    external_refs = Column(JSON, default=dict)  # Shopify, WooCommerce, etc. product IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="products")
    created_by = relationship("User")
    stock_moves = relationship("StockMove", back_populates="product", cascade="all, delete-orphan")
    order_line_items = relationship("OrderLineItem", back_populates="product")
    
    @property
    def available_quantity(self):
        """Get available stock quantity"""
        return max(0, self.stock_quantity - self.reserved_quantity)
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.track_inventory and self.available_quantity <= self.reorder_point
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<Product {self.name} ({self.sku})>"


class StockLocation(Base):
    """Stock/Warehouse location model"""
    __tablename__ = "stock_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, index=True)
    type = Column(String(50), default="warehouse")  # warehouse, store, supplier, customer
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Contact Information
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    properties = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="stock_locations")
    stock_moves_from = relationship("StockMove", foreign_keys="StockMove.from_location_id", back_populates="from_location")
    stock_moves_to = relationship("StockMove", foreign_keys="StockMove.to_location_id", back_populates="to_location")
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<StockLocation {self.name}>"


class StockMove(Base):
    """Stock movement/transaction model"""
    __tablename__ = "stock_moves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Movement Details
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    from_location_id = Column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True)
    to_location_id = Column(UUID(as_uuid=True), ForeignKey("stock_locations.id"), nullable=True)
    
    # Quantities and Costs
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Movement Type and Reference
    movement_type = Column(String(50), nullable=False)  # purchase, sale, transfer, adjustment, return
    reference_type = Column(String(50), nullable=True)  # order, invoice, adjustment, etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status and Notes
    status = Column(String(20), default="completed")  # pending, completed, cancelled
    notes = Column(Text, nullable=True)
    
    # Metadata
    moved_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company")
    product = relationship("Product", back_populates="stock_moves")
    from_location = relationship("StockLocation", foreign_keys=[from_location_id], back_populates="stock_moves_from")
    to_location = relationship("StockLocation", foreign_keys=[to_location_id], back_populates="stock_moves_to")
    created_by = relationship("User")
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<StockMove {self.movement_type} {self.quantity} of {self.product.name if self.product else 'Unknown'}>"
