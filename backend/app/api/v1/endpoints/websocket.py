"""
TECHGURU ElevateCRM WebSocket Endpoints

Real-time WebSocket connections with tenant isolation for live updates.
Handles stock changes, order updates, notifications, and user activities.
"""
import json
import asyncio
import logging
from typing import Dict, Set, Optional, List
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.dependencies import get_current_user, get_current_tenant_context
from ....core.tenant_context import TenantContext
from ....models.user import User
from app.services.realtime_service import get_realtime_service, RealtimeService, RealtimeEvent
from ....services.tenant_service import TenantAwareService

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections with tenant isolation"""
    
    def __init__(self):
        # Active connections: tenant_id -> {user_id -> {connection_id -> websocket}}
        self.active_connections: Dict[str, Dict[str, Dict[str, WebSocket]]] = {}
        # Connection metadata: connection_id -> {user_id, tenant_id, connected_at}
        self.connection_metadata: Dict[str, Dict] = {}
        
    def generate_connection_id(self) -> str:
        """Generate unique connection ID"""
        return str(uuid.uuid4())
    
    async def connect(self, websocket: WebSocket, user_id: str, tenant_id: str) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        connection_id = self.generate_connection_id()
        
        # Initialize tenant connections if needed
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}
        
        # Initialize user connections if needed
        if user_id not in self.active_connections[tenant_id]:
            self.active_connections[tenant_id][user_id] = {}
        
        # Store connection
        self.active_connections[tenant_id][user_id][connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        logger.info(f"✅ WebSocket connected: user={user_id}, tenant={tenant_id}, conn={connection_id}")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[connection_id]
        user_id = metadata["user_id"]
        tenant_id = metadata["tenant_id"]
        
        # Remove from active connections
        if (tenant_id in self.active_connections and 
            user_id in self.active_connections[tenant_id] and 
            connection_id in self.active_connections[tenant_id][user_id]):
            
            del self.active_connections[tenant_id][user_id][connection_id]
            
            # Clean up empty structures
            if not self.active_connections[tenant_id][user_id]:
                del self.active_connections[tenant_id][user_id]
                
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        
        # Remove metadata
        del self.connection_metadata[connection_id]
        
        logger.info(f"❌ WebSocket disconnected: user={user_id}, tenant={tenant_id}, conn={connection_id}")
    
    async def send_to_user(self, tenant_id: str, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if (tenant_id not in self.active_connections or 
            user_id not in self.active_connections[tenant_id]):
            return
        
        connections = self.active_connections[tenant_id][user_id]
        disconnected = []
        
        for connection_id, websocket in connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def send_to_tenant(self, tenant_id: str, message: dict, exclude_user: Optional[str] = None):
        """Send message to all users in a tenant"""
        if tenant_id not in self.active_connections:
            return
        
        for user_id in list(self.active_connections[tenant_id].keys()):
            if exclude_user and user_id == exclude_user:
                continue
                
            await self.send_to_user(tenant_id, user_id, message)
    
    async def broadcast(self, message: dict, exclude_tenant: Optional[str] = None):
        """Send message to all connected users across all tenants"""
        for tenant_id in list(self.active_connections.keys()):
            if exclude_tenant and tenant_id == exclude_tenant:
                continue
                
            await self.send_to_tenant(tenant_id, message)
    
    def get_tenant_user_count(self, tenant_id: str) -> int:
        """Get number of connected users for a tenant"""
        if tenant_id not in self.active_connections:
            return 0
        return len(self.active_connections[tenant_id])
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return len(self.connection_metadata)
    
    def get_user_connections(self, tenant_id: str, user_id: str) -> int:
        """Get number of connections for a specific user"""
        if (tenant_id not in self.active_connections or 
            user_id not in self.active_connections[tenant_id]):
            return 0
        return len(self.active_connections[tenant_id][user_id])


# Global connection manager
connection_manager = ConnectionManager()


async def get_websocket_auth(
    websocket: WebSocket,
    token: Optional[str] = None
) -> tuple[User, TenantContext]:
    """Authenticate WebSocket connection"""
    if not token:
        # Try to get token from query parameters
        token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Use existing auth dependencies (adapt as needed)
        # This is a simplified version - you may need to adapt based on your auth system
        from ....core.auth import verify_token
        from ....core.dependencies import get_db_session
        
        payload = verify_token(token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        if not user_id or not tenant_id:
            await websocket.close(code=4001, reason="Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create user and tenant context objects
        user = User(id=user_id)  # Simplified - you may want to fetch full user
        tenant_context = TenantContext(
            tenant_id=tenant_id,
            user_id=user_id,
            company_id=tenant_id  # Assuming tenant_id is company_id
        )
        
        return user, tenant_context
        
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
    realtime_service: RealtimeService = Depends(get_realtime_service)
):
    """Main WebSocket endpoint for real-time communication"""
    user = None
    tenant_context = None
    connection_id = None
    
    try:
        # Authenticate connection
        user, tenant_context = await get_websocket_auth(websocket, token)
        
        # Connect to manager
        connection_id = await connection_manager.connect(
            websocket, 
            user.id, 
            tenant_context.tenant_id
        )
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "connection_id": connection_id,
            "user_id": user.id,
            "tenant_id": tenant_context.tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Start listening for real-time events from Redis
        asyncio.create_task(
            listen_for_events(
                realtime_service, 
                tenant_context.tenant_id, 
                user.id, 
                connection_id
            )
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Handle different message types
                await handle_client_message(
                    data, 
                    user, 
                    tenant_context, 
                    connection_id, 
                    realtime_service
                )
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally: {connection_id}")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Failed to process message",
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during setup")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=4000, reason="Internal error")
    
    finally:
        # Clean up connection
        if connection_id:
            connection_manager.disconnect(connection_id)


async def handle_client_message(
    data: dict, 
    user: User, 
    tenant_context: TenantContext,
    connection_id: str,
    realtime_service: RealtimeService
):
    """Handle incoming messages from WebSocket clients"""
    message_type = data.get("type")
    
    if message_type == "ping":
        # Handle ping/pong for connection health
        await connection_manager.send_to_user(
            tenant_context.tenant_id,
            user.id,
            {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    elif message_type == "subscribe":
        # Handle subscription to specific event types
        event_types = data.get("event_types", [])
        logger.info(f"User {user.id} subscribing to events: {event_types}")
        
        # Send confirmation
        await connection_manager.send_to_user(
            tenant_context.tenant_id,
            user.id,
            {
                "type": "subscription_confirmed",
                "event_types": event_types,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    elif message_type == "activity":
        # Handle user activity tracking
        activity_data = data.get("data", {})
        
        await realtime_service.publish_user_activity(
            tenant_context.tenant_id,
            user.id,
            activity_data.get("activity_type", "unknown"),
            activity_data
        )
    
    else:
        logger.warning(f"Unknown message type: {message_type}")


async def listen_for_events(
    realtime_service: RealtimeService,
    tenant_id: str,
    user_id: str,
    connection_id: str
):
    """Listen for Redis events and forward to WebSocket"""
    try:
        async def event_callback(event: RealtimeEvent):
            """Callback for real-time events"""
            message = {
                "type": "realtime_event",
                "event_type": event.event_type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "event_id": event.event_id
            }
            
            await connection_manager.send_to_user(tenant_id, user_id, message)
        
        # Subscribe to all event types for this tenant
        event_types = [
            "stock_update",
            "order_update", 
            "user_activity",
            "notification",
            "contact_update",
            "product_update",
            "dashboard_refresh"
        ]
        
        await realtime_service.subscribe_to_tenant_events(
            tenant_id,
            event_types,
            event_callback
        )
        
    except Exception as e:
        logger.error(f"Error in event listener for {connection_id}: {e}")


# Health check endpoint for WebSocket status
@router.get("/ws/health")
async def websocket_health():
    """Health check for WebSocket service"""
    return {
        "status": "healthy",
        "total_connections": connection_manager.get_total_connections(),
        "active_tenants": len(connection_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }


# Admin endpoint to get connection stats
@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    stats = {
        "total_connections": connection_manager.get_total_connections(),
        "tenants": {}
    }
    
    for tenant_id in connection_manager.active_connections:
        stats["tenants"][tenant_id] = {
            "users": len(connection_manager.active_connections[tenant_id]),
            "total_connections": sum(
                len(connections) 
                for connections in connection_manager.active_connections[tenant_id].values()
            )
        }
    
    return stats