"""
TECHGURU ElevateCRM Development Seed Data Script

Creates sample data for development and testing purposes.
Safe to run multiple times (idempotent).
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import initialize_database
from app.core import database
from app.models import Company, User, Contact, Product, StockLocation, Order, Integration

# Demo data constants
DEMO_COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
DEMO_ADMIN_ID = "550e8400-e29b-41d4-a716-446655440001"

async def create_demo_company():
    """Create demo company if it doesn't exist"""
    if database.AsyncSessionLocal is None:
        raise Exception("Database not initialized - AsyncSessionLocal is None")
    async with database.AsyncSessionLocal() as session:
        # Check if company already exists
        existing = await session.get(Company, DEMO_COMPANY_ID)
        if existing:
            print(f"✓ Demo company already exists: {existing.name}")
            return existing

        company = Company(
            id=uuid.UUID(DEMO_COMPANY_ID),
            name="TECHGURU Demo Company", 
            subdomain="demo",
            email="admin@techguru.com",
            phone="+1 (555) 123-4567",
            website="https://techguru.com",
            address_line1="123 Business Avenue",
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="USA",
            timezone="America/Los_Angeles",
            currency="USD",
            subscription_plan="enterprise",
            subscription_expires_at=datetime.utcnow() + timedelta(days=365),
            settings={
                "features": {
                    "inventory_management": True,
                    "crm": True,
                    "integrations": True,
                    "reporting": True
                },
                "ui_preferences": {
                    "default_theme": "light",
                    "sidebar_collapsed": False
                }
            }
        )
        
        session.add(company)
        await session.commit()
        print(f"✓ Created demo company: {company.name}")
        return company


async def create_demo_admin():
    """Create demo admin user if doesn't exist"""
    async with database.AsyncSessionLocal() as session:
        # Check if admin already exists
        existing = await session.get(User, DEMO_ADMIN_ID)
        if existing:
            print(f"✓ Demo admin already exists: {existing.email}")
            return existing

        admin = User(
            id=uuid.UUID(DEMO_ADMIN_ID),
            company_id=uuid.UUID(DEMO_COMPANY_ID),
            email="admin@techguru.com",
            external_id="demo-admin-keycloak-id",
            first_name="Demo",
            last_name="Administrator",
            display_name="Demo Admin",
            phone="+1 (555) 123-4567",
            title="System Administrator",
            department="IT",
            roles=["admin", "user", "manager"],
            permissions=["*"],  # All permissions
            is_active=True,
            is_verified=True,
            timezone="America/Los_Angeles",
            language="en",
            last_login_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        session.add(admin)
        await session.commit()
        print(f"✓ Created demo admin: {admin.email}")
        return admin


async def create_demo_contacts():
    """Create sample contacts"""
    contacts_data = [
        {
            "first_name": "John",
            "last_name": "Smith", 
            "email": "john.smith@acmecorp.com",
            "phone": "+1 (555) 234-5678",
            "company_name": "ACME Corporation",
            "lifecycle_stage": "customer",
            "industry": "Technology",
            "lead_score": Decimal("85.5")
        },
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah@innovatetech.com", 
            "phone": "+1 (555) 345-6789",
            "company_name": "InnovateTech",
            "lifecycle_stage": "prospect",
            "industry": "Software",
            "lead_score": Decimal("72.0")
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "m.brown@globalcorp.com",
            "phone": "+1 (555) 456-7890", 
            "company_name": "Global Corp",
            "lifecycle_stage": "lead",
            "industry": "Manufacturing",
            "lead_score": Decimal("45.5")
        }
    ]

    async with database.AsyncSessionLocal() as session:
        created_count = 0
        
        for contact_data in contacts_data:
            # Check if contact already exists by email
            from sqlalchemy import select
            result = await session.execute(
                select(Contact).where(
                    Contact.email == contact_data["email"],
                    Contact.company_id == uuid.UUID(DEMO_COMPANY_ID)
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                continue

            contact = Contact(
                company_id=uuid.UUID(DEMO_COMPANY_ID),
                created_by_id=uuid.UUID(DEMO_ADMIN_ID),
                type="individual",
                **contact_data,
                address_line1="456 Client Street",
                city="Los Angeles", 
                state="CA",
                postal_code="90210",
                country="USA",
                properties={
                    "source": "demo_seed",
                    "preferences": {"email_marketing": True}
                },
                tags=["demo", "seed_data"]
            )
            
            session.add(contact)
            created_count += 1
        
        if created_count > 0:
            await session.commit()
            print(f"✓ Created {created_count} demo contacts")
        else:
            print("✓ Demo contacts already exist")


async def create_demo_products():
    """Create sample products"""
    products_data = [
        {
            "name": "Wireless Bluetooth Headphones",
            "sku": "WBH-001",
            "barcode": "123456789012",
            "description": "Premium noise-canceling wireless headphones",
            "category": "Electronics",
            "subcategory": "Audio",
            "brand": "TECHGURU",
            "cost_price": Decimal("45.00"),
            "sale_price": Decimal("99.99"),
            "weight": Decimal("0.250"),
            "stock_quantity": 150,
            "reorder_point": 25,
            "reorder_quantity": 100
        },
        {
            "name": "USB-C Charging Cable",
            "sku": "USB-C-001", 
            "barcode": "123456789013",
            "description": "6ft USB-C to USB-C fast charging cable",
            "category": "Electronics",
            "subcategory": "Cables",
            "brand": "TECHGURU",
            "cost_price": Decimal("3.50"),
            "sale_price": Decimal("12.99"),
            "weight": Decimal("0.100"),
            "stock_quantity": 500,
            "reorder_point": 50,
            "reorder_quantity": 200
        },
        {
            "name": "Software License - CRM Pro",
            "sku": "SW-CRM-PRO",
            "description": "Annual CRM Pro software license",
            "type": "service",
            "category": "Software",
            "subcategory": "Licenses",
            "brand": "TECHGURU",
            "cost_price": Decimal("100.00"),
            "sale_price": Decimal("299.00"),
            "track_inventory": False
        }
    ]

    async with database.AsyncSessionLocal() as session:
        created_count = 0
        
        for product_data in products_data:
            # Check if product already exists by SKU
            from sqlalchemy import select
            result = await session.execute(
                select(Product).where(
                    Product.sku == product_data["sku"],
                    Product.company_id == uuid.UUID(DEMO_COMPANY_ID)
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                continue

            product = Product(
                company_id=uuid.UUID(DEMO_COMPANY_ID),
                created_by_id=uuid.UUID(DEMO_ADMIN_ID),
                **product_data,
                properties={
                    "source": "demo_seed",
                    "featured": product_data["sku"] == "WBH-001"
                },
                external_refs={"demo_seed": True}
            )
            
            session.add(product)
            created_count += 1
        
        if created_count > 0:
            await session.commit()
            print(f"✓ Created {created_count} demo products")
        else:
            print("✓ Demo products already exist")


async def create_demo_stock_location():
    """Create default stock location"""
    async with database.AsyncSessionLocal() as session:
        # Check if default location exists
        from sqlalchemy import select
        result = await session.execute(
            select(StockLocation).where(
                StockLocation.company_id == uuid.UUID(DEMO_COMPANY_ID),
                StockLocation.is_default == True
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✓ Default stock location already exists: {existing.name}")
            return

        location = StockLocation(
            company_id=uuid.UUID(DEMO_COMPANY_ID),
            name="Main Warehouse",
            code="MAIN-WH",
            type="warehouse",
            address_line1="789 Warehouse Drive",
            city="San Francisco",
            state="CA", 
            postal_code="94107",
            country="USA",
            contact_name="Warehouse Manager",
            phone="+1 (555) 789-0123",
            email="warehouse@techguru.com",
            is_default=True
        )
        
        session.add(location)
        await session.commit()
        print(f"✓ Created default stock location: {location.name}")


async def create_demo_integration():
    """Create sample integration"""
    async with database.AsyncSessionLocal() as session:
        # Check if integration exists
        from sqlalchemy import select
        result = await session.execute(
            select(Integration).where(
                Integration.company_id == uuid.UUID(DEMO_COMPANY_ID),
                Integration.provider == "shopify"
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✓ Demo integration already exists: {existing.name}")
            return

        integration = Integration(
            company_id=uuid.UUID(DEMO_COMPANY_ID),
            created_by_id=uuid.UUID(DEMO_ADMIN_ID),
            name="Demo Shopify Store",
            provider="shopify",
            type="ecommerce",
            status="inactive",
            config={
                "shop_domain": "demo-store.myshopify.com",
                "api_version": "2023-10"
            },
            credentials={
                "note": "Demo integration - not connected to real Shopify"
            },
            sync_enabled=False
        )
        
        session.add(integration)
        await session.commit()
        print(f"✓ Created demo integration: {integration.name}")


async def seed_database():
    """Run all seed data creation"""
    print("🌱 Starting database seeding...")
    
    # Initialize database connection
    print("🔌 Initializing database connection...")
    db_init_result = initialize_database()
    print(f"🔌 Database init result: {db_init_result}")
    
    if not db_init_result:
        print("❌ Database not available - PostgreSQL server must be running")
        print("💡 To start PostgreSQL:")
        print("   1. Install PostgreSQL from https://www.postgresql.org/download/")
        print("   2. Start PostgreSQL service")
        print("   3. Create database: createdb techguru_crm")
        print("   4. Run migrations: alembic upgrade head")
        print("   5. Then run seeding again")
        return False
        
    # Check if AsyncSessionLocal was created
    print(f"🔌 AsyncSessionLocal: {database.AsyncSessionLocal}")
    if database.AsyncSessionLocal is None:
        print("❌ AsyncSessionLocal is None even though init returned True")
        return False
    
    try:
        # Create seed data in order
        print("🏢 Creating demo company...")
        await create_demo_company()
        print("👤 Creating demo admin...")
        await create_demo_admin()
        print("📞 Creating demo contacts...")
        await create_demo_contacts()
        print("📦 Creating demo products...")
        await create_demo_products() 
        print("🏪 Creating stock location...")
        await create_demo_stock_location()
        print("🔗 Creating demo integration...")
        await create_demo_integration()
        
        print("✅ Database seeding completed successfully!")
        print("\n📋 Demo Login Information:")
        print(f"   Email: admin@techguru.com")
        print(f"   Tenant ID: {DEMO_COMPANY_ID}")
        print(f"   Company: TECHGURU Demo Company")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run seeding script
    asyncio.run(seed_database())
