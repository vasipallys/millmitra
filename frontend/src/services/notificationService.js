/**
 * Loads mill notifications from the API and keeps the bell live via SSE.
 * Stream uses fetch + Authorization (EventSource cannot set headers).
 * If the stream drops, the list is polled every 15 seconds.
 */

import api from './api';

const POLL_MS = 15000;

function apiBase() {
  return import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
}

function authToken() {
  return localStorage.getItem('token');
}

function normalize(item) {
  if (!item) return item;
  const body = item.body || item.message || '';
  const created = item.created_at || item.timestamp;
  return {
    ...item,
    body,
    message: body,
    severity: item.severity || item.priority || 'medium',
    priority: item.severity || item.priority || 'medium',
    link: item.link || item.action_url,
    action_url: item.link || item.action_url,
    created_at: created,
    timestamp: created,
    read: Boolean(item.read || item.read_at),
  };
}

class NotificationService {
  constructor() {
    this.notifications = [];
    this.listeners = [];
    this.unreadCount = 0;
    this.pollInterval = null;
    this.started = false;
    this.streamActive = false;
    this.abortStream = null;
  }

  start() {
    if (!authToken()) {
      this.resetLocal();
      return;
    }
    this.fetchNotifications();
    if (!this.started) {
      this.started = true;
      this.connectStream();
    } else if (!this.streamActive && !this.pollInterval) {
      this.connectStream();
    }
  }

  resetLocal() {
    this.notifications = [];
    this.unreadCount = 0;
    this.notifyListeners();
  }

  async fetchNotifications() {
    if (!authToken()) {
      this.resetLocal();
      return;
    }
    try {
      const response = await api.get('/notifications');
      const data = response.data || {};
      const items = Array.isArray(data.notifications) ? data.notifications.map(normalize) : [];
      this.notifications = items;
      this.unreadCount = typeof data.unread_count === 'number'
        ? data.unread_count
        : items.filter((item) => !item.read).length;
      this.notifyListeners();
    } catch (error) {
      this.resetLocal();
    }
  }

  prepend(raw) {
    const item = normalize(raw);
    if (!item || item.id == null) return;
    if (this.notifications.some((existing) => existing.id === item.id)) return;
    this.notifications = [item, ...this.notifications];
    this.unreadCount = this.notifications.filter((row) => !row.read).length;
    this.notifyListeners();
  }

  async connectStream() {
    const token = authToken();
    if (!token) return;
    if (this.abortStream) {
      this.abortStream.abort();
    }
    const controller = new AbortController();
    this.abortStream = controller;
    try {
      const response = await fetch(`${apiBase()}/notifications/stream`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      });
      if (!response.ok || !response.body) {
        throw new Error('stream unavailable');
      }
      this.streamActive = true;
      this.clearPoll();
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop() || '';
        chunks.forEach((chunk) => {
          const line = chunk.split('\n').find((row) => row.startsWith('data:'));
          if (!line) return;
          try {
            const payload = JSON.parse(line.slice(5).trim() || '{}');
            if (payload.notification) {
              this.prepend(payload.notification);
            }
          } catch (error) {
            // Ignore a partial or keepalive frame.
          }
        });
      }
      throw new Error('stream closed');
    } catch (error) {
      if (controller.signal.aborted) return;
      this.streamActive = false;
      this.startPoll();
    }
  }

  startPoll() {
    if (this.pollInterval) return;
    this.pollInterval = setInterval(() => {
      this.fetchNotifications();
    }, POLL_MS);
  }

  clearPoll() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  getNotifications() {
    return this.notifications;
  }

  getUnreadCount() {
    return this.unreadCount;
  }

  async markAsRead(notificationId) {
    const notification = this.notifications.find((item) => item.id === notificationId);
    if (notification && !notification.read) {
      notification.read = true;
      notification.read_at = notification.read_at || new Date().toISOString();
      this.unreadCount = this.notifications.filter((item) => !item.read).length;
      this.notifyListeners();
    }
    try {
      await api.post(`/notifications/${notificationId}/read`);
    } catch (error) {
      this.fetchNotifications();
    }
  }

  async markAllAsRead() {
    this.notifications.forEach((item) => {
      item.read = true;
    });
    this.unreadCount = 0;
    this.notifyListeners();
    try {
      await api.post('/notifications/mark-all-read');
    } catch (error) {
      this.fetchNotifications();
    }
  }

  async deleteNotification(notificationId) {
    const index = this.notifications.findIndex((item) => item.id === notificationId);
    if (index !== -1) {
      this.notifications.splice(index, 1);
      this.unreadCount = this.notifications.filter((item) => !item.read).length;
      this.notifyListeners();
    }
    try {
      await api.delete(`/notifications/${notificationId}`);
    } catch (error) {
      this.fetchNotifications();
    }
  }

  getNotificationsByCategory(category) {
    return this.notifications.filter((item) => item.category === category);
  }

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  notifyListeners() {
    this.listeners.forEach((callback) => {
      try {
        callback({
          notifications: this.notifications,
          unreadCount: this.unreadCount,
        });
      } catch (error) {
        // A listener should not break the others.
      }
    });
  }

  destroy() {
    this.clearPoll();
    if (this.abortStream) {
      this.abortStream.abort();
      this.abortStream = null;
    }
    this.streamActive = false;
    this.started = false;
    this.listeners = [];
  }
}

const notificationService = new NotificationService();

export default notificationService;
