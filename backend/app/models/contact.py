"""
TECHGURU ElevateCRM Contact Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from sqlalchemy.orm import relationship

from app.core.database import Base


class Contact(Base):
    """Contact/Lead/Customer model"""
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Basic Information
    type = Column(String(50), default="individual")  # individual, company, lead
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    display_name = Column(String(200), nullable=True)
    
    # Contact Information
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # CRM Fields
    lifecycle_stage = Column(String(50), default="lead")  # lead, prospect, customer, partner
    lead_source = Column(String(100), nullable=True)
    lead_score = Column(Numeric(10, 2), default=0)
    
    # Business Information
    industry = Column(String(100), nullable=True)
    annual_revenue = Column(Numeric(15, 2), nullable=True)
    employee_count = Column(String(50), nullable=True)
    
    # Custom Fields and Properties
    properties = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    
    # Status and Assignment
    is_active = Column(Boolean, default=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Activity Tracking
    last_contacted_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_contacts")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_contacts")
    orders = relationship("Order", back_populates="contact", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get contact's full name"""
        if self.type == "company":
            return self.company_name
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.email or "Unknown Contact"
    
    @property 
    def tenant_id(self):
        """Get tenant ID for RLS"""
        return self.company_id
    
    def __repr__(self):
        return f"<Contact {self.full_name}>"
