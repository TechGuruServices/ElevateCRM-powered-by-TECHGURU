"""
TECHGURU ElevateCRM User Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model with RBAC and multi-tenant support"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), nullable=False, index=True)
    external_id = Column(String(255), nullable=True)  # From Keycloak/Auth0
    
    # Profile Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True) 
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Contact Information
    phone = Column(String(50), nullable=True)
    title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Permissions and Roles
    roles = Column(JSON, default=list)
    permissions = Column(JSON, default=list)
    
    # Status and Preferences
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Activity Tracking
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    created_by = relationship("User", remote_side=[id])
    created_contacts = relationship("Contact", foreign_keys="Contact.created_by_id", back_populates="created_by")
    assigned_contacts = relationship("Contact", foreign_keys="Contact.assigned_to_id", back_populates="assigned_to")
    created_orders = relationship("Order", foreign_keys="Order.created_by_id", back_populates="created_by")
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.email
    
    @property
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<User {self.email}>"
