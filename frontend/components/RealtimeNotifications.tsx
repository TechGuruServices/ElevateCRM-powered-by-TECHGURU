/**
 * TECHGURU ElevateCRM Real-time Notifications Component
 * 
 * Displays live notifications for stock updates, order changes, and system alerts.
 * Features toast notifications with automatic dismissal and real-time event handling.
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Bell, Package, ShoppingCart, AlertCircle, CheckCircle, X } from 'lucide-react';
import { useNotifications, useStockUpdates, useOrderUpdates } from '../hooks/useRealtime';

interface Notification {
  id: string;
  type: 'stock' | 'order' | 'system' | 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  autoHide?: boolean;
  data?: any;
}

interface RealtimeNotificationsProps {
  className?: string;
  maxNotifications?: number;
  autoHideDelay?: number;
  showBadge?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export default function RealtimeNotifications({
  className = '',
  maxNotifications = 10,
  autoHideDelay = 5000,
  showBadge = true,
  position = 'top-right'
}: RealtimeNotificationsProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Create notification from event data
  const createNotification = useCallback((
    type: Notification['type'],
    title: string,
    message: string,
    priority: Notification['priority'] = 'normal',
    data?: any,
    autoHide: boolean = true
  ): Notification => {
    return {
      id: `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      title,
      message,
      timestamp: new Date(),
      read: false,
      priority,
      autoHide,
      data
    };
  }, []);

  // Add notification to the list
  const addNotification = useCallback((notification: Notification) => {
    setNotifications(prev => {
      const updated = [notification, ...prev].slice(0, maxNotifications);
      return updated;
    });
    
    setUnreadCount(prev => prev + 1);

    // Auto-hide notification after delay
    if (notification.autoHide && autoHideDelay > 0) {
      setTimeout(() => {
        removeNotification(notification.id);
      }, autoHideDelay);
    }
  }, [maxNotifications, autoHideDelay]);

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Mark notification as read
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  // Mark all as read
  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  }, []);

  // Handle stock updates
  useStockUpdates(useCallback((stockData: any) => {
    const { product_id, old_quantity, new_quantity, change, location_id } = stockData;
    
    let title = 'Stock Updated';
    let message = `Product ${product_id}: `;
    let priority: Notification['priority'] = 'normal';
    
    if (change > 0) {
      message += `+${change} units added`;
      priority = 'normal';
    } else if (change < 0) {
      message += `${change} units removed`;
      priority = change < -10 ? 'high' : 'normal';
    } else {
      message += 'transferred between locations';
    }
    
    if (location_id) {
      message += ` at location ${location_id}`;
    }
    
    // High priority for low stock warnings
    if (new_quantity < 10) {
      title = 'Low Stock Alert';
      priority = 'high';
    }
    
    const notification = createNotification('stock', title, message, priority, stockData);
    addNotification(notification);
  }, [createNotification, addNotification]));

  // Handle order updates
  useOrderUpdates(useCallback((orderData: any) => {
    const { order_id, status, previous_status } = orderData;
    
    const statusLabels: Record<string, string> = {
      'pending': 'Pending',
      'confirmed': 'Confirmed',
      'processing': 'Processing',
      'shipped': 'Shipped',
      'delivered': 'Delivered',
      'cancelled': 'Cancelled'
    };
    
    const title = 'Order Status Update';
    const message = `Order ${order_id} changed from ${statusLabels[previous_status] || previous_status} to ${statusLabels[status] || status}`;
    
    let priority: Notification['priority'] = 'normal';
    if (status === 'cancelled') priority = 'high';
    if (status === 'delivered') priority = 'low';
    
    const notification = createNotification('order', title, message, priority, orderData);
    addNotification(notification);
  }, [createNotification, addNotification]));

  // Handle system notifications
  useNotifications(useCallback((notificationData: any) => {
    const { notification_type, title, message, priority = 'normal' } = notificationData;
    
    let type: Notification['type'] = 'system';
    
    // Map notification types
    switch (notification_type) {
      case 'stock_movement':
        type = 'stock';
        break;
      case 'order_update':
        type = 'order';
        break;
      case 'system_alert':
        type = 'system';
        break;
      case 'user_activity':
        type = 'info';
        break;
      default:
        type = 'system';
    }
    
    const notification = createNotification(type, title, message, priority, notificationData);
    addNotification(notification);
  }, [createNotification, addNotification]));

  // Get icon for notification type
  const getNotificationIcon = (type: Notification['type']) => {
    const iconClass = "w-5 h-5";
    
    switch (type) {
      case 'stock':
        return <Package className={iconClass} />;
      case 'order':
        return <ShoppingCart className={iconClass} />;
      case 'success':
        return <CheckCircle className={iconClass} />;
      case 'warning':
      case 'error':
        return <AlertCircle className={iconClass} />;
      default:
        return <Bell className={iconClass} />;
    }
  };

  // Get notification color classes
  const getNotificationColors = (type: Notification['type'], priority: Notification['priority']) => {
    const baseClasses = "border-l-4";
    
    if (priority === 'urgent' || priority === 'high') {
      return `${baseClasses} border-red-500 bg-red-50 text-red-900`;
    }
    
    switch (type) {
      case 'stock':
        return `${baseClasses} border-blue-500 bg-blue-50 text-blue-900`;
      case 'order':
        return `${baseClasses} border-green-500 bg-green-50 text-green-900`;
      case 'success':
        return `${baseClasses} border-emerald-500 bg-emerald-50 text-emerald-900`;
      case 'warning':
        return `${baseClasses} border-yellow-500 bg-yellow-50 text-yellow-900`;
      case 'error':
        return `${baseClasses} border-red-500 bg-red-50 text-red-900`;
      default:
        return `${baseClasses} border-gray-500 bg-gray-50 text-gray-900`;
    }
  };

  // Position classes
  const getPositionClasses = () => {
    const baseClasses = "fixed z-50";
    
    switch (position) {
      case 'top-left':
        return `${baseClasses} top-4 left-4`;
      case 'top-right':
        return `${baseClasses} top-4 right-4`;
      case 'bottom-left':
        return `${baseClasses} bottom-4 left-4`;
      case 'bottom-right':
        return `${baseClasses} bottom-4 right-4`;
      default:
        return `${baseClasses} top-4 right-4`;
    }
  };

  return (
    <div className={`${className}`}>
      {/* Notification Bell Button */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-6 h-6" />
          {showBadge && unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>

        {/* Notifications Dropdown */}
        {isOpen && (
          <div className="absolute right-0 top-full mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-techguru-blue hover:text-techguru-dark transition-colors"
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 transition-colors ${
                        !notification.read ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`flex-shrink-0 ${getNotificationColors(notification.type, notification.priority).split(' ').find(c => c.includes('text-'))}`}>
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {notification.title}
                            </p>
                            <p className="text-xs text-gray-500">
                              {notification.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {notification.message}
                          </p>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                          )}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeNotification(notification.id);
                          }}
                          className="flex-shrink-0 text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Toast Notifications */}
      <div className={getPositionClasses()}>
        <div className="space-y-2">
          {notifications
            .filter(n => !n.read && n.autoHide)
            .slice(0, 3) // Show max 3 toasts
            .map((notification) => (
              <div
                key={`toast_${notification.id}`}
                className={`${getNotificationColors(notification.type, notification.priority)} 
                  p-4 rounded-lg shadow-lg max-w-sm animate-slide-in`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{notification.title}</p>
                    <p className="text-sm mt-1 opacity-90">{notification.message}</p>
                  </div>
                  <button
                    onClick={() => removeNotification(notification.id)}
                    className="flex-shrink-0 opacity-70 hover:opacity-100"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}