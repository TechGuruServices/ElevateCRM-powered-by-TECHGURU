23#!/usr/bin/env python3
"""
Test Tenant Isolation

Verifies that the SQLite-compatible tenant isolation is working correctly.
"""
import sys
import os
import asyncio
import uuid
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.core.tenant_context import TenantContextManager
from app.services.tenant_service import TenantAwareService
from app.models.company import Company
from app.models.user import User
from app.models.contact import Contact


async def test_tenant_isolation():
    """Test tenant isolation functionality"""
    print("🧪 Testing Tenant Isolation...")
    
    # Create engine for testing
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create test session
    async with engine.begin() as conn:
        # Create async session
        session = AsyncSession(conn, expire_on_commit=False)
        service = TenantAwareService(session)
        
        try:
            # Create two test companies (tenants)
            print("\n📊 Creating test companies...")
            
            # Tenant A
            TenantContextManager.clear_tenant_id()  # Clear context first
            company_a_id = uuid.uuid4()
            company_a = Company(
                id=company_a_id,
                name="Test Company A",
                subdomain="test-a"
            )
            session.add(company_a)
            await session.flush()
            
            # Tenant B  
            company_b_id = uuid.uuid4()
            company_b = Company(
                id=company_b_id,
                name="Test Company B",
                subdomain="test-b"
            )
            session.add(company_b)
            await session.flush()
            
            print(f"✅ Created Company A: {company_a_id}")
            print(f"✅ Created Company B: {company_b_id}")
            
            # Test 1: Create contacts for each tenant
            print("\n👤 Testing contact creation with tenant context...")
            
            # Create test users first (contacts require created_by_id)
            test_user_a_id = uuid.uuid4()
            test_user_a = User(
                id=test_user_a_id,
                company_id=company_a_id,
                email="admin@company-a.com",
                first_name="Admin",
                last_name="A"
            )
            session.add(test_user_a)
            await session.flush()
            
            test_user_b_id = uuid.uuid4()
            test_user_b = User(
                id=test_user_b_id,
                company_id=company_b_id,
                email="admin@company-b.com",
                first_name="Admin", 
                last_name="B"
            )
            session.add(test_user_b)
            await session.flush()
            
            # Set tenant A context and create contact
            TenantContextManager.set_tenant_id(str(company_a_id))
            contact_a = await service.create(
                Contact,
                first_name="John",
                last_name="Doe",
                email="john@company-a.com",
                type="person",
                created_by_id=test_user_a_id
            )
            print(f"✅ Created contact for Tenant A: {contact_a.id}")
            
            # Set tenant B context and create contact
            TenantContextManager.set_tenant_id(str(company_b_id))
            contact_b = await service.create(
                Contact,
                first_name="Jane",
                last_name="Smith", 
                email="jane@company-b.com",
                type="person",
                created_by_id=test_user_b_id
            )
            print(f"✅ Created contact for Tenant B: {contact_b.id}")
            
            # Test 2: Verify isolation - Tenant A should only see their contact
            print("\n🔒 Testing tenant isolation...")
            
            TenantContextManager.set_tenant_id(str(company_a_id))
            contacts_a = await service.get_all(Contact)
            print(f"📋 Tenant A sees {len(contacts_a)} contacts")
            assert len(contacts_a) == 1
            assert contacts_a[0].email == "john@company-a.com"
            print("✅ Tenant A isolation verified")
            
            # Test 3: Verify isolation - Tenant B should only see their contact
            TenantContextManager.set_tenant_id(str(company_b_id))
            contacts_b = await service.get_all(Contact)
            print(f"📋 Tenant B sees {len(contacts_b)} contacts")
            assert len(contacts_b) == 1
            assert contacts_b[0].email == "jane@company-b.com"
            print("✅ Tenant B isolation verified")
            
            # Test 4: No tenant context should return no results
            print("\n🚫 Testing no tenant context...")
            TenantContextManager.clear_tenant_id()
            contacts_none = await service.get_all(Contact)
            print(f"📋 No tenant context sees {len(contacts_none)} contacts")
            assert len(contacts_none) == 0
            print("✅ No-context isolation verified")
            
            # Test 5: Cross-tenant access should be denied
            print("\n🛡️  Testing cross-tenant access prevention...")
            TenantContextManager.set_tenant_id(str(company_a_id))
            # Try to get contact B by ID (should return None due to tenant filtering)
            cross_access_contact = await service.get_by_id(Contact, contact_b.id)
            assert cross_access_contact is None
            print("✅ Cross-tenant access blocked")
            
            # Test 6: Test search with tenant filtering
            print("\n🔍 Testing search with tenant filtering...")
            TenantContextManager.set_tenant_id(str(company_a_id))
            search_results = await service.search(
                Contact,
                search_fields=["first_name", "email"],
                search_term="john"
            )
            assert len(search_results) == 1
            assert search_results[0].first_name == "John"
            print("✅ Tenant-filtered search verified")
            
            # Test 7: Test update with tenant validation
            print("\n✏️  Testing update with tenant validation...")
            updated_contact = await service.update(
                Contact,
                contact_a.id,
                last_name="Updated"
            )
            assert updated_contact is not None
            assert updated_contact.last_name == "Updated"
            print("✅ Tenant-validated update verified")
            
            # Test 8: Test count with tenant filtering
            print("\n📊 Testing count with tenant filtering...")
            count_a = await service.count(Contact)
            assert count_a == 1
            TenantContextManager.set_tenant_id(str(company_b_id))
            count_b = await service.count(Contact)
            assert count_b == 1
            print("✅ Tenant-filtered count verified")
            
            print("\n🎉 All tenant isolation tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise
        finally:
            await session.rollback()  # Don't commit test data
            await engine.dispose()  # Clean up engine


if __name__ == "__main__":
    asyncio.run(test_tenant_isolation())
