#!/usr/bin/env python3
"""
Test Inventory + Barcode Features

Tests the inventory endpoints and barcode functionality.
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
from app.models.product import Product, StockLocation, StockMove


async def test_inventory_system():
    """Test inventory and barcode functionality"""
    print("🏪 Testing Inventory + Barcode System...")

    # Create engine for testing
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create test session
    async with engine.begin() as conn:
        session = AsyncSession(conn, expire_on_commit=False)
        service = TenantAwareService(session)

        try:
            # Create test company and user
            print("\n📊 Setting up test environment...")
            
            company_id = uuid.uuid4()
            company = Company(
                id=company_id,
                name="Test Inventory Company",
                subdomain="test-inventory"
            )
            session.add(company)
            await session.flush()

            TenantContextManager.set_tenant_id(str(company_id))

            user_id = uuid.uuid4()
            user = User(
                id=user_id,
                company_id=company_id,
                email="inventory@test.com",
                first_name="Inventory",
                last_name="Manager"
            )
            session.add(user)
            await session.flush()

            print(f"✅ Created company: {company_id}")
            print(f"✅ Created user: {user_id}")

            # Test 1: Create stock location
            print("\n📍 Testing stock location creation...")
            
            location = await service.create(
                StockLocation,
                name="Main Warehouse",
                code="MAIN-WH",
                type="warehouse",
                is_active=True,
                is_default=True
            )
            print(f"✅ Created stock location: {location.name}")

            # Test 2: Create products with barcodes
            print("\n📦 Testing product creation with barcodes...")
            
            product_a = await service.create(
                Product,
                name="Test Product A",
                sku="TEST-001",
                barcode="1234567890123",
                sale_price=29.99,
                track_inventory=True,
                stock_quantity=100,
                created_by_id=user_id
            )
            
            product_b = await service.create(
                Product,
                name="Test Product B", 
                sku="TEST-002",
                barcode="9876543210987",
                sale_price=15.50,
                track_inventory=True,
                stock_quantity=50,
                created_by_id=user_id
            )
            
            print(f"✅ Created Product A: {product_a.name} (Barcode: {product_a.barcode})")
            print(f"✅ Created Product B: {product_b.name} (Barcode: {product_b.barcode})")

            # Test 3: Test barcode search
            print("\n🔍 Testing barcode search...")
            
            # Search by barcode
            found_products = await service.search(
                Product,
                search_fields=["barcode"],
                search_term="1234567890123"
            )
            
            assert len(found_products) == 1
            assert found_products[0].name == "Test Product A"
            print("✅ Barcode search working correctly")

            # Test 4: Create stock movements
            print("\n📈 Testing stock movements...")
            
            # Purchase (stock in)
            purchase_move = await service.create(
                StockMove,
                product_id=product_a.id,
                to_location_id=location.id,
                quantity=50,
                unit_cost=20.00,
                total_cost=1000.00,
                movement_type="purchase",
                reference_type="order",
                status="completed",
                created_by_id=user_id
            )
            
            # Sale (stock out)
            sale_move = await service.create(
                StockMove,
                product_id=product_a.id,
                from_location_id=location.id,
                quantity=-10,
                unit_cost=29.99,
                total_cost=299.90,
                movement_type="sale",
                reference_type="order",
                status="completed",
                created_by_id=user_id
            )
            
            print(f"✅ Created purchase move: +{purchase_move.quantity} units")
            print(f"✅ Created sale move: {sale_move.quantity} units")

            # Test 5: Get stock moves for product
            print("\n📋 Testing stock move queries...")
            
            all_moves = await service.get_all(
                StockMove,
                filters={"product_id": product_a.id}
            )
            
            assert len(all_moves) == 2
            print(f"✅ Found {len(all_moves)} stock moves for product")

            # Test 6: Test invalid barcode search
            print("\n❌ Testing invalid barcode search...")
            
            invalid_search = await service.search(
                Product,
                search_fields=["barcode"],
                search_term="9999999999999"
            )
            
            assert len(invalid_search) == 0
            print("✅ Invalid barcode correctly returns no results")

            # Test 7: Test stock transfer
            print("\n🔄 Testing stock transfer...")
            
            # Create second location
            location_b = await service.create(
                StockLocation,
                name="Secondary Warehouse",
                code="SEC-WH",
                type="warehouse",
                is_active=True
            )
            
            # Transfer stock
            transfer_move = await service.create(
                StockMove,
                product_id=product_b.id,
                from_location_id=location.id,
                to_location_id=location_b.id,
                quantity=25,
                movement_type="transfer",
                reference_type="adjustment",
                status="completed",
                created_by_id=user_id
            )
            
            print(f"✅ Created transfer: {transfer_move.quantity} units from {location.name} to {location_b.name}")

            # Test 8: Get all products with barcodes
            print("\n📊 Testing product inventory summary...")
            
            all_products = await service.get_all(Product)
            barcode_products = [p for p in all_products if p.barcode]
            
            print(f"✅ Found {len(barcode_products)} products with barcodes:")
            for product in barcode_products:
                print(f"   - {product.name}: {product.barcode} (Stock: {product.stock_quantity})")

            print("\n🎉 All inventory + barcode tests passed!")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise
        finally:
            await session.rollback()  # Don't commit test data
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_inventory_system())