"""
TECHGURU ElevateCRM Inventory API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime

from app.core.dependencies import get_async_db, get_current_user
from app.models.product import Product, StockLocation, StockMove
from app.core.tenant_context import TenantContextManager
from app.services.tenant_service import TenantAwareService
from app.services.realtime_service import get_realtime_service, RealtimeService
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas
class StockLocationCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    type: str = "warehouse"
    address: Optional[str] = None
    is_active: bool = True
    is_sellable: bool = True
    is_default: bool = False


class StockLocationResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    code: str
    description: Optional[str]
    type: str
    address: Optional[str]
    is_active: bool
    is_sellable: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockMoveCreate(BaseModel):
    product_id: uuid.UUID
    from_location_id: Optional[uuid.UUID] = None
    to_location_id: Optional[uuid.UUID] = None
    quantity: int
    unit_cost: Optional[float] = None
    movement_type: str  # purchase, sale, transfer, adjustment, return
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class StockMoveResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    product_id: uuid.UUID
    from_location_id: Optional[uuid.UUID]
    to_location_id: Optional[uuid.UUID]
    quantity: int
    unit_cost: Optional[float]
    total_cost: Optional[float]
    movement_type: str
    reference_type: Optional[str]
    reference_id: Optional[uuid.UUID]
    status: str
    notes: Optional[str]
    moved_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class BarcodeSearchResponse(BaseModel):
    product: Optional[dict] = None
    found: bool = False
    barcode: str


class StockSummaryResponse(BaseModel):
    product_id: uuid.UUID
    product_name: str
    product_sku: str
    barcode: Optional[str]
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    locations: List[dict]


# Stock Locations endpoints
@router.get("/locations", response_model=List[StockLocationResponse])
async def get_stock_locations(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all stock locations for the current tenant"""
    service = TenantAwareService(db)
    locations = await service.get_all(StockLocation, skip=skip, limit=limit)
    return locations


@router.post("/locations", response_model=StockLocationResponse)
async def create_stock_location(
    location_data: StockLocationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user)
):
    """Create a new stock location"""
    service = TenantAwareService(db)
    
    # Check if code is unique within company
    existing = await service.search(
        StockLocation,
        search_fields=["code"],
        search_term=location_data.code
    )
    if existing:
        raise HTTPException(status_code=400, detail="Location code already exists")
    
    location = await service.create(StockLocation, **location_data.dict())
    return location


@router.get("/locations/{location_id}", response_model=StockLocationResponse)
async def get_stock_location(
    location_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user)
):
    """Get a specific stock location"""
    service = TenantAwareService(db)
    location = await service.get_by_id(StockLocation, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Stock location not found")
    return location


# Stock Moves endpoints
@router.get("/moves", response_model=List[StockMoveResponse])
async def get_stock_moves(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    product_id: Optional[uuid.UUID] = Query(None),
    location_id: Optional[uuid.UUID] = Query(None),
    move_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get stock moves with optional filters"""
    service = TenantAwareService(db)
    
    # Build filters
    filters = {}
    if product_id:
        filters["product_id"] = product_id
    if move_type:
        filters["movement_type"] = move_type
    
    moves = await service.get_all(StockMove, filters=filters, limit=limit, offset=skip)
    return moves


@router.post("/moves", response_model=StockMoveResponse)
async def create_stock_move(
    move_data: StockMoveCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    realtime_service: RealtimeService = Depends(get_realtime_service)
):
    """Create a new stock movement"""
    service = TenantAwareService(db)
    
    # Validate product exists
    product = await service.get_by_id(Product, move_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get current stock level before move
    old_quantity = 0
    if move_data.from_location_id:
        # This is an outbound move - get current stock at from_location
        current_stock_query = select(func.sum(StockMove.quantity)).where(
            and_(
                StockMove.product_id == move_data.product_id,
                StockMove.to_location_id == move_data.from_location_id,
                StockMove.company_id == service.tenant_context.company_id
            )
        )
        current_stock_result = await db.execute(current_stock_query)
        old_quantity = current_stock_result.scalar() or 0
    
    # Validate locations if provided
    if move_data.from_location_id:
        from_location = await service.get_by_id(StockLocation, move_data.from_location_id)
        if not from_location:
            raise HTTPException(status_code=404, detail="From location not found")
    
    if move_data.to_location_id:
        to_location = await service.get_by_id(StockLocation, move_data.to_location_id)
        if not to_location:
            raise HTTPException(status_code=404, detail="To location not found")
    
    # Calculate total cost
    data = move_data.dict()
    if data.get("unit_cost") and data.get("quantity"):
        data["total_cost"] = data["unit_cost"] * data["quantity"]
    
    # Add processed metadata
    data["created_by_id"] = current_user.id
    data["moved_at"] = datetime.utcnow()
    data["status"] = "completed"
    
    move = await service.create(StockMove, **data)
    
    # Calculate new stock level and publish real-time event
    new_quantity = old_quantity
    if move_data.from_location_id and move_data.to_location_id:
        # Transfer between locations - no net change but still notify
        await realtime_service.publish_stock_update(
            service.tenant_context.company_id,
            str(move_data.product_id),
            old_quantity,
            old_quantity,  # Same quantity but transferred
            str(move_data.from_location_id)
        )
    elif move_data.to_location_id:
        # Stock in - increase
        new_quantity = old_quantity + move_data.quantity
        await realtime_service.publish_stock_update(
            service.tenant_context.company_id,
            str(move_data.product_id),
            old_quantity,
            new_quantity,
            str(move_data.to_location_id)
        )
    elif move_data.from_location_id:
        # Stock out - decrease
        new_quantity = old_quantity - move_data.quantity
        await realtime_service.publish_stock_update(
            service.tenant_context.company_id,
            str(move_data.product_id),
            old_quantity,
            new_quantity,
            str(move_data.from_location_id)
        )
    
    # Also publish a general notification
    await realtime_service.publish_system_notification(
        service.tenant_context.company_id,
        "stock_movement",
        "Stock Movement Created",
        f"Stock movement for {product.name}: {move_data.quantity} units",
        "normal"
    )
    
    return move


# Barcode scanning endpoints
@router.get("/barcode/{barcode}", response_model=BarcodeSearchResponse)
async def search_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user)
):
    """Search for a product by barcode"""
    service = TenantAwareService(db)
    
    # Search for product with this barcode
    products = await service.search(
        Product,
        search_fields=["barcode"],
        search_term=barcode
    )
    
    if products:
        product = products[0]
        return BarcodeSearchResponse(
            product={
                "id": str(product.id),
                "name": product.name,
                "sku": product.sku,
                "barcode": product.barcode,
                "sale_price": float(product.sale_price) if product.sale_price else None,
                "stock_quantity": product.stock_quantity
            },
            found=True,
            barcode=barcode
        )
    else:
        return BarcodeSearchResponse(
            found=False,
            barcode=barcode
        )


@router.post("/barcode/create-product")
async def create_product_from_barcode(
    barcode: str,
    name: str,
    sku: str,
    sale_price: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user)
):
    """Create a new product with the scanned barcode"""
    service = TenantAwareService(db)
    
    # Check if barcode already exists
    existing = await service.search(
        Product,
        search_fields=["barcode"],
        search_term=barcode
    )
    if existing:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists")
    
    # Check if SKU already exists
    existing_sku = await service.search(
        Product,
        search_fields=["sku"],
        search_term=sku
    )
    if existing_sku:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    product_data = {
        "name": name,
        "sku": sku,
        "barcode": barcode,
        "sale_price": sale_price or 0,
        "track_inventory": True,
        "created_by_id": current_user.id
    }
    
    product = await service.create(Product, **product_data)
    return {"product": product, "message": "Product created successfully"}


# Stock summary and reports
@router.get("/summary", response_model=List[StockSummaryResponse])
async def get_stock_summary(
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    location_id: Optional[uuid.UUID] = Query(None),
    low_stock_only: bool = Query(False)
):
    """Get stock summary by product and location"""
    tenant_id = TenantContextManager.get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    # This would require a more complex query, for now return simplified version
    service = TenantAwareService(db)
    products = await service.get_all(Product, limit=1000)
    
    summary = []
    for product in products:
        if low_stock_only and product.stock_quantity > product.reorder_point:
            continue
            
        summary.append(StockSummaryResponse(
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            barcode=product.barcode,
            total_quantity=product.stock_quantity,
            available_quantity=product.stock_quantity - product.reserved_quantity,
            reserved_quantity=product.reserved_quantity,
            locations=[{"name": "Main Warehouse", "quantity": product.stock_quantity}]
        ))
    
    return summary


@router.post("/moves/{move_id}/confirm")
async def confirm_stock_move(
    move_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user)
):
    """Confirm a pending stock move"""
    service = TenantAwareService(db)
    
    move = await service.get_by_id(StockMove, move_id)
    if not move:
        raise HTTPException(status_code=404, detail="Stock move not found")
    
    if move.status != "pending":
        raise HTTPException(status_code=400, detail="Stock move is not pending")
    
    # Update the move status
    updated_move = await service.update(
        StockMove,
        move_id,
        status="confirmed",
        processed_at=datetime.utcnow(),
        processed_by_id=current_user.id
    )
    
    return {"message": "Stock move confirmed", "move": updated_move}