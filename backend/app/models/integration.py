"""
TECHGURU ElevateCRM Integration Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Integration(Base):
    """Integration model for external service connections"""
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Integration Details
    name = Column(String(255), nullable=False)  # "Shopify Store", "QuickBooks Online"
    provider = Column(String(100), nullable=False, index=True)  # shopify, quickbooks, stripe, etc.
    type = Column(String(50), nullable=False)  # ecommerce, accounting, payment, email, etc.
    
    # Configuration
    config = Column(JSON, default=dict)  # API keys, endpoints, settings
    credentials = Column(JSON, default=dict)  # Encrypted tokens, secrets
    
    # Status and Health
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    status = Column(String(50), default="inactive")  # inactive, active, error, expired
    
    # Sync Configuration
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(50), default="hourly")  # manual, realtime, hourly, daily
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    
    # Error Handling
    error_count = Column(String(10), default="0")
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="integrations")
    created_by = relationship("User")
    webhooks = relationship("Webhook", back_populates="integration", cascade="all, delete-orphan")
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<Integration {self.name} ({self.provider})>"


class Webhook(Base):
    """Webhook model for incoming and outgoing webhooks"""
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Webhook Details
    direction = Column(String(20), nullable=False)  # incoming, outgoing
    event_type = Column(String(100), nullable=False)  # order.created, product.updated, etc.
    url = Column(String(500), nullable=True)  # For outgoing webhooks
    
    # Request/Response Data
    headers = Column(JSON, default=dict)
    payload = Column(JSON, default=dict)
    response_status = Column(String(10), nullable=True)
    response_body = Column(Text, nullable=True)
    
    # Status and Timing
    status = Column(String(50), default="pending")  # pending, success, failed, retry
    attempts = Column(String(10), default="0")
    processed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = relationship("Integration", back_populates="webhooks")
    
    def __repr__(self):
        return f"<Webhook {self.event_type} ({self.direction})>"
