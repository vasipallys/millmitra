/**
 * Notification Service
 * Handles real-time notifications, alerts, and system messages
 */

import api from './api';

class NotificationService {
  constructor() {
    this.notifications = [];
    this.listeners = [];
    this.unreadCount = 0;
    this.setupEventSource();
  }

  /**
   * Setup Server-Sent Events for real-time notifications
   */
  setupEventSource() {
    // In a real implementation, this would connect to a WebSocket or SSE endpoint
    // For now, we'll simulate with periodic polling
    this.pollInterval = setInterval(() => {
      this.fetchNotifications();
    }, 30000); // Poll every 30 seconds
  }

  /**
   * Fetch notifications from backend
   */
  async fetchNotifications() {
    try {
      const response = await api.get('/notifications');
      if (response.data.success) {
        this.notifications = response.data.notifications;
        this.unreadCount = response.data.unread_count;
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      // Fallback to mock data if API fails
      this.loadMockNotifications();
    }
  }

  /**
   * Load mock notifications for development
   */
  loadMockNotifications() {
    const mockNotifications = [
      {
        id: 1,
        type: 'farmer_registration',
        title: 'New Farmer Registration',
        message: 'Siva Kumar reddy Vasipally has registered and is pending approval',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        read: false,
        priority: 'medium',
        category: 'farmer_management',
        action_url: '/farmers',
        icon: 'person_add'
      },
      {
        id: 2,
        type: 'production_complete',
        title: 'Production Batch Completed',
        message: 'Production batch #PB001 has been completed successfully',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        read: false,
        priority: 'low',
        category: 'production',
        action_url: '/production',
        icon: 'check_circle'
      },
      {
        id: 3,
        type: 'inventory_alert',
        title: 'Low Stock Alert',
        message: 'Basmati Rice stock is running low (Current: 50 kg, Minimum: 100 kg)',
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        read: false,
        priority: 'high',
        category: 'inventory',
        action_url: '/inventory',
        icon: 'warning'
      },
      {
        id: 4,
        type: 'quality_alert',
        title: 'Quality Check Required',
        message: 'Batch #QC001 requires immediate quality inspection',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        read: true,
        priority: 'high',
        category: 'quality',
        action_url: '/quality-control',
        icon: 'science'
      },
      {
        id: 5,
        type: 'payment_received',
        title: 'Payment Received',
        message: 'Payment of ₹25,000 received from ABC Distributors',
        timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
        read: true,
        priority: 'low',
        category: 'finance',
        action_url: '/finance',
        icon: 'payment'
      },
      {
        id: 6,
        type: 'system_update',
        title: 'System Update Available',
        message: 'A new system update (v2.1.0) is available with enhanced AI features',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        read: false,
        priority: 'medium',
        category: 'system',
        action_url: '/settings',
        icon: 'system_update'
      }
    ];

    this.notifications = mockNotifications;
    this.unreadCount = mockNotifications.filter(n => !n.read).length;
    this.notifyListeners();
  }

  /**
   * Get all notifications
   */
  getNotifications() {
    return this.notifications;
  }

  /**
   * Get unread notifications count
   */
  getUnreadCount() {
    return this.unreadCount;
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId) {
    try {
      await api.post(`/notifications/${notificationId}/read`);
      
      // Update local state
      const notification = this.notifications.find(n => n.id === notificationId);
      if (notification && !notification.read) {
        notification.read = true;
        this.unreadCount = Math.max(0, this.unreadCount - 1);
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
      // Update locally even if API fails
      const notification = this.notifications.find(n => n.id === notificationId);
      if (notification && !notification.read) {
        notification.read = true;
        this.unreadCount = Math.max(0, this.unreadCount - 1);
        this.notifyListeners();
      }
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead() {
    try {
      await api.post('/notifications/mark-all-read');
      
      // Update local state
      this.notifications.forEach(n => n.read = true);
      this.unreadCount = 0;
      this.notifyListeners();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      // Update locally even if API fails
      this.notifications.forEach(n => n.read = true);
      this.unreadCount = 0;
      this.notifyListeners();
    }
  }

  /**
   * Delete notification
   */
  async deleteNotification(notificationId) {
    try {
      await api.delete(`/notifications/${notificationId}`);
      
      // Update local state
      const index = this.notifications.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        const notification = this.notifications[index];
        if (!notification.read) {
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
        this.notifications.splice(index, 1);
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  }

  /**
   * Get notifications by category
   */
  getNotificationsByCategory(category) {
    return this.notifications.filter(n => n.category === category);
  }

  /**
   * Get notifications by priority
   */
  getNotificationsByPriority(priority) {
    return this.notifications.filter(n => n.priority === priority);
  }

  /**
   * Subscribe to notification updates
   */
  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Notify all listeners of changes
   */
  notifyListeners() {
    this.listeners.forEach(callback => {
      try {
        callback({
          notifications: this.notifications,
          unreadCount: this.unreadCount
        });
      } catch (error) {
        console.error('Error in notification listener:', error);
      }
    });
  }

  /**
   * Create new notification (for testing)
   */
  createNotification(notification) {
    const newNotification = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      read: false,
      priority: 'medium',
      category: 'system',
      ...notification
    };

    this.notifications.unshift(newNotification);
    if (!newNotification.read) {
      this.unreadCount++;
    }
    this.notifyListeners();
  }

  /**
   * Initialize service
   */
  init() {
    this.loadMockNotifications();
  }

  /**
   * Cleanup
   */
  destroy() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
    this.listeners = [];
  }
}

// Create and export singleton instance
const notificationService = new NotificationService();

// Initialize on import
notificationService.init();

export default notificationService;
