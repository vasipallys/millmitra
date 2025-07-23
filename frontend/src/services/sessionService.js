/**
 * Session Management Service
 * Handles user sessions, authentication state, and security
 */

import api from './api';

class SessionService {
  constructor() {
    this.sessionToken = localStorage.getItem('sessionToken');
    this.setupInterceptors();
  }

  /**
   * Setup API interceptors for session management
   */
  setupInterceptors() {
    // Request interceptor to add session token
    api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        const sessionToken = localStorage.getItem('sessionToken');
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        if (sessionToken) {
          config.headers['X-Session-Token'] = sessionToken;
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle session responses
    api.interceptors.response.use(
      (response) => {
        // Update session token if provided in response headers
        const newSessionToken = response.headers['x-session-token'];
        if (newSessionToken) {
          this.setSessionToken(newSessionToken);
        }
        
        return response;
      },
      (error) => {
        // Handle session expiration
        if (error.response?.status === 401) {
          this.clearSession();
          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set session token
   */
  setSessionToken(token) {
    this.sessionToken = token;
    if (token) {
      localStorage.setItem('sessionToken', token);
    } else {
      localStorage.removeItem('sessionToken');
    }
  }

  /**
   * Get current session token
   */
  getSessionToken() {
    return this.sessionToken || localStorage.getItem('sessionToken');
  }

  /**
   * Clear session data
   */
  clearSession() {
    this.sessionToken = null;
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  /**
   * Get active sessions for current user
   */
  async getActiveSessions() {
    try {
      const response = await api.get('/session/active');
      return response.data;
    } catch (error) {
      console.error('Error fetching active sessions:', error);
      throw error;
    }
  }

  /**
   * Invalidate a specific session
   */
  async invalidateSession(sessionId) {
    try {
      const response = await api.post(`/session/invalidate/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error invalidating session:', error);
      throw error;
    }
  }

  /**
   * Invalidate all sessions except current
   */
  async invalidateAllSessions() {
    try {
      const response = await api.post('/session/invalidate-all');
      return response.data;
    } catch (error) {
      console.error('Error invalidating all sessions:', error);
      throw error;
    }
  }

  /**
   * Extend current session
   */
  async extendSession() {
    try {
      const response = await api.post('/session/extend');
      return response.data;
    } catch (error) {
      console.error('Error extending session:', error);
      throw error;
    }
  }

  /**
   * Get current session information
   */
  async getSessionInfo() {
    try {
      const response = await api.get('/session/info');
      return response.data;
    } catch (error) {
      console.error('Error fetching session info:', error);
      throw error;
    }
  }

  /**
   * Update session security level
   */
  async updateSessionSecurity(securityLevel) {
    try {
      const response = await api.post('/session/security/update', {
        security_level: securityLevel
      });
      return response.data;
    } catch (error) {
      console.error('Error updating session security:', error);
      throw error;
    }
  }

  /**
   * Get session statistics (admin only)
   */
  async getSessionStats() {
    try {
      const response = await api.get('/session/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching session stats:', error);
      throw error;
    }
  }

  /**
   * Clean up expired sessions (admin only)
   */
  async cleanupExpiredSessions() {
    try {
      const response = await api.post('/session/cleanup');
      return response.data;
    } catch (error) {
      console.error('Error cleaning up sessions:', error);
      throw error;
    }
  }

  /**
   * Check if session is valid
   */
  async validateSession() {
    try {
      const response = await api.get('/auth/me');
      return response.data.success;
    } catch (error) {
      return false;
    }
  }

  /**
   * Auto-extend session on user activity
   */
  setupAutoExtend() {
    let lastActivity = Date.now();
    const EXTEND_INTERVAL = 5 * 60 * 1000; // 5 minutes
    const ACTIVITY_THRESHOLD = 10 * 60 * 1000; // 10 minutes

    // Track user activity
    const updateActivity = () => {
      lastActivity = Date.now();
    };

    // Add event listeners for user activity
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true });
    });

    // Auto-extend session periodically
    setInterval(async () => {
      const timeSinceActivity = Date.now() - lastActivity;
      
      if (timeSinceActivity < ACTIVITY_THRESHOLD && this.getSessionToken()) {
        try {
          await this.extendSession();
        } catch (error) {
          console.warn('Failed to extend session:', error);
        }
      }
    }, EXTEND_INTERVAL);
  }

  /**
   * Get device information for session tracking
   */
  getDeviceInfo() {
    return {
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Initialize session management
   */
  init() {
    // Setup auto-extend if session exists
    if (this.getSessionToken()) {
      this.setupAutoExtend();
    }

    // Validate session on page load
    this.validateSession().then(isValid => {
      if (!isValid && this.getSessionToken()) {
        this.clearSession();
      }
    });
  }
}

// Create and export singleton instance
const sessionService = new SessionService();

// Initialize on import
sessionService.init();

export default sessionService;
