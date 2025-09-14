"""
TECHGURU ElevateCRM Real-time Service

Redis-based pub/sub system for real-time updates across the platform.
Handles stock level changes, order updates, and other real-time events.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Set
from dataclasses import dataclass
from datetime import datetime
import uuid

import redis.asyncio as redis
from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RealtimeEvent:
    """Real-time event data structure"""
    event_type: str
    tenant_id: str
    data: Dict[str, Any]
    timestamp: datetime
    event_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tenant_id": self.tenant_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RealtimeEvent":
        return cls(
            event_type=data["event_type"],
            tenant_id=data["tenant_id"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_id=data.get("event_id")
        )


class RealtimeService:
    """Redis-based real-time pub/sub service"""
    
    def __init__(self):
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.subscriptions: Dict[str, Set[Callable]] = {}
        self.is_connected = False
        
    async def connect(self):
        """Initialize Redis connection"""
        try:
            # Create Redis connection pool
            self.redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                retry_on_timeout=True,
                decode_responses=True
            )
            
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            
            logger.info("✅ Connected to Redis for real-time service")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.aclose()
        if self.redis_pool:
            await self.redis_pool.aclose()
        self.is_connected = False
        logger.info("Disconnected from Redis")
    
    def _get_channel_name(self, event_type: str, tenant_id: str) -> str:
        """Generate Redis channel name for tenant-specific events"""
        return f"elevatecrm:{tenant_id}:{event_type}"
    
    def _get_global_channel_name(self, event_type: str) -> str:
        """Generate Redis channel name for global events"""
        return f"elevatecrm:global:{event_type}"
    
    async def publish_event(self, event: RealtimeEvent):
        """Publish an event to Redis"""
        if not self.is_connected:
            logger.warning("Redis not connected, skipping event publish")
            return
            
        try:
            # Tenant-specific channel
            tenant_channel = self._get_channel_name(event.event_type, event.tenant_id)
            
            # Global channel for system-wide events
            global_channel = self._get_global_channel_name(event.event_type)
            
            event_data = json.dumps(event.to_dict())
            
            # Publish to both channels
            await self.redis_client.publish(tenant_channel, event_data)
            await self.redis_client.publish(global_channel, event_data)
            
            logger.debug(f"Published event {event.event_type} for tenant {event.tenant_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    async def subscribe_to_tenant_events(
        self, 
        tenant_id: str, 
        event_types: list[str],
        callback: Callable[[RealtimeEvent], None]
    ):
        """Subscribe to events for a specific tenant"""
        if not self.is_connected:
            await self.connect()
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to tenant-specific channels
            channels = [self._get_channel_name(event_type, tenant_id) for event_type in event_types]
            
            for channel in channels:
                await pubsub.subscribe(channel)
                logger.info(f"Subscribed to channel: {channel}")
            
            # Listen for messages
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        event = RealtimeEvent.from_dict(event_data)
                        
                        # Call the callback function
                        await callback(event)
                        
                    except Exception as e:
                        logger.error(f"Error processing real-time event: {e}")
                        
        except Exception as e:
            logger.error(f"Error in event subscription: {e}")
    
    # Convenience methods for common events
    
    async def publish_stock_update(self, tenant_id: str, product_id: str, 
                                 old_quantity: int, new_quantity: int, 
                                 location_id: Optional[str] = None):
        """Publish stock level update event"""
        event = RealtimeEvent(
            event_type="stock_update",
            tenant_id=tenant_id,
            data={
                "product_id": product_id,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "location_id": location_id,
                "change": new_quantity - old_quantity
            },
            timestamp=datetime.utcnow()
        )
        await self.publish_event(event)
    
    async def publish_order_update(self, tenant_id: str, order_id: str, 
                                 status: str, previous_status: Optional[str] = None):
        """Publish order status update event"""
        event = RealtimeEvent(
            event_type="order_update",
            tenant_id=tenant_id,
            data={
                "order_id": order_id,
                "status": status,
                "previous_status": previous_status
            },
            timestamp=datetime.utcnow()
        )
        await self.publish_event(event)
    
    async def publish_user_activity(self, tenant_id: str, user_id: str, 
                                  activity_type: str, details: Dict[str, Any]):
        """Publish user activity event"""
        event = RealtimeEvent(
            event_type="user_activity",
            tenant_id=tenant_id,
            data={
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details
            },
            timestamp=datetime.utcnow()
        )
        await self.publish_event(event)
    
    async def publish_system_notification(self, tenant_id: str, 
                                        notification_type: str, 
                                        title: str, message: str,
                                        priority: str = "normal"):
        """Publish system notification event"""
        event = RealtimeEvent(
            event_type="notification",
            tenant_id=tenant_id,
            data={
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "priority": priority
            },
            timestamp=datetime.utcnow()
        )
        await self.publish_event(event)


# Global instance
realtime_service = RealtimeService()


async def get_realtime_service() -> RealtimeService:
    """Dependency injection for real-time service"""
    if not realtime_service.is_connected:
        await realtime_service.connect()
    return realtime_service


# Event type constants
class EventTypes:
    STOCK_UPDATE = "stock_update"
    ORDER_UPDATE = "order_update"
    USER_ACTIVITY = "user_activity"
    NOTIFICATION = "notification"
    CONTACT_UPDATE = "contact_update"
    PRODUCT_UPDATE = "product_update"
    DASHBOARD_REFRESH = "dashboard_refresh"