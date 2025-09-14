/**
 * TECHGURU ElevateCRM Real-time WebSocket Hook
 * 
 * Custom React hook for managing WebSocket connections and real-time updates.
 * Provides automatic reconnection, event handling, and tenant isolation.
 */
'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth'; // Assuming you have an auth hook

export interface RealtimeEvent {
  event_type: string;
  data: any;
  timestamp: string;
  event_id: string;
}

export interface WebSocketMessage {
  type: string;
  event_type?: string;
  data?: any;
  timestamp: string;
  event_id?: string;
  connection_id?: string;
  user_id?: string;
  tenant_id?: string;
}

export interface UseRealtimeOptions {
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

export interface UseRealtimeReturn {
  isConnected: boolean;
  connectionId: string | null;
  error: string | null;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  subscribe: (eventTypes: string[]) => void;
  lastEvent: RealtimeEvent | null;
}

const DEFAULT_OPTIONS: UseRealtimeOptions = {
  autoConnect: true,
  reconnectAttempts: 5,
  reconnectDelay: 2000,
  heartbeatInterval: 30000,
  debug: false,
};

export function useRealtime(
  onEvent?: (event: RealtimeEvent) => void,
  options: UseRealtimeOptions = {}
): UseRealtimeReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const { user, isAuthenticated } = useAuth(); // Get authentication data
  const token = 'demo-token'; // Mock token for demo purposes
  
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isManualDisconnectRef = useRef(false);

  const log = useCallback((message: string, data?: any) => {
    if (opts.debug) {
      console.log(`[WebSocket] ${message}`, data || '');
    }
  }, [opts.debug]);

  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }
    
    heartbeatTimeoutRef.current = setTimeout(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().toISOString()
        }));
        startHeartbeat(); // Schedule next heartbeat
      }
    }, opts.heartbeatInterval);
  }, [opts.heartbeatInterval]);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      log('Received message:', message);

      switch (message.type) {
        case 'connection_established':
          setConnectionId(message.connection_id || null);
          setIsConnected(true);
          setError(null);
          reconnectCountRef.current = 0;
          startHeartbeat();
          log('Connection established:', message.connection_id);
          break;

        case 'pong':
          log('Received pong');
          break;

        case 'realtime_event':
          if (message.event_type && message.data) {
            const realtimeEvent: RealtimeEvent = {
              event_type: message.event_type,
              data: message.data,
              timestamp: message.timestamp,
              event_id: message.event_id || '',
            };
            
            setLastEvent(realtimeEvent);
            onEvent?.(realtimeEvent);
            log('Real-time event:', realtimeEvent);
          }
          break;

        case 'subscription_confirmed':
          log('Subscription confirmed:', message.data);
          break;

        case 'error':
          setError(message.data?.message || 'WebSocket error');
          log('Error from server:', message.data);
          break;

        default:
          log('Unknown message type:', message.type);
      }
    } catch (err) {
      log('Failed to parse message:', err);
      setError('Failed to parse server message');
    }
  }, [onEvent, log, startHeartbeat]);

  const handleError = useCallback((event: Event) => {
    log('WebSocket error:', event);
    setError('WebSocket connection error');
  }, [log]);

  const handleClose = useCallback((event: CloseEvent) => {
    log('WebSocket closed:', { code: event.code, reason: event.reason });
    
    setIsConnected(false);
    setConnectionId(null);
    clearTimeouts();

    // Don't reconnect if manually disconnected
    if (isManualDisconnectRef.current) {
      isManualDisconnectRef.current = false;
      return;
    }

    // Attempt reconnection if within limits
    if (reconnectCountRef.current < opts.reconnectAttempts!) {
      const delay = opts.reconnectDelay! * Math.pow(2, reconnectCountRef.current);
      
      log(`Attempting reconnection ${reconnectCountRef.current + 1}/${opts.reconnectAttempts} in ${delay}ms`);
      
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectCountRef.current++;
        connect();
      }, delay);
    } else {
      setError('Max reconnection attempts reached');
      log('Max reconnection attempts reached');
    }
  }, [opts.reconnectAttempts, opts.reconnectDelay, clearTimeouts, log]);

  const connect = useCallback(() => {
    if (!user || !token) {
      log('Cannot connect: missing user or token');
      setError('Authentication required');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.CONNECTING || 
        wsRef.current?.readyState === WebSocket.OPEN) {
      log('WebSocket already connecting or connected');
      return;
    }

    try {
      // Use secure WebSocket in production
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = process.env.NODE_ENV === 'production' 
        ? window.location.host 
        : 'localhost:8000';
      
      const wsUrl = `${protocol}//${host}/api/v1/realtime/ws?token=${encodeURIComponent(token)}`;
      
      log('Connecting to:', wsUrl.replace(/token=[^&]+/, 'token=***'));
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        log('WebSocket connected');
      };
      
      wsRef.current.onmessage = handleMessage;
      wsRef.current.onerror = handleError;
      wsRef.current.onclose = handleClose;
      
    } catch (err) {
      log('Failed to create WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [user, token, handleMessage, handleError, handleClose, log]);

  const disconnect = useCallback(() => {
    log('Manually disconnecting WebSocket');
    isManualDisconnectRef.current = true;
    clearTimeouts();
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionId(null);
    setError(null);
  }, [clearTimeouts, log]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString()
      }));
      log('Sent message:', message);
    } else {
      log('Cannot send message: WebSocket not connected');
      setError('WebSocket not connected');
    }
  }, [log]);

  const subscribe = useCallback((eventTypes: string[]) => {
    sendMessage({
      type: 'subscribe',
      event_types: eventTypes
    });
  }, [sendMessage]);

  // Auto-connect on mount if enabled and user is authenticated
  useEffect(() => {
    if (opts.autoConnect && user && token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [opts.autoConnect, user, token, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimeouts();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [clearTimeouts]);

  return {
    isConnected,
    connectionId,
    error,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    lastEvent,
  };
}

// Specialized hook for stock updates
export function useStockUpdates(onStockUpdate?: (update: any) => void) {
  return useRealtime((event) => {
    if (event.event_type === 'stock_update') {
      onStockUpdate?.(event.data);
    }
  });
}

// Specialized hook for order updates
export function useOrderUpdates(onOrderUpdate?: (update: any) => void) {
  return useRealtime((event) => {
    if (event.event_type === 'order_update') {
      onOrderUpdate?.(event.data);
    }
  });
}

// Specialized hook for notifications
export function useNotifications(onNotification?: (notification: any) => void) {
  return useRealtime((event) => {
    if (event.event_type === 'notification') {
      onNotification?.(event.data);
    }
  });
}