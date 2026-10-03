import api from './api';

const API_BASE = '/auth';

class AuthService {
  async login(credentials) {
    try {
      // Add device info to login request
      const deviceInfo = this.getDeviceInfo();
      const loginData = {
        ...credentials,
        device_info: deviceInfo
      };

      const response = await api.post(`${API_BASE}/login`, loginData);

      if (response.data.requires_2fa) {
        return response.data;
      }

      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));

        if (response.data.session_token) {
          localStorage.setItem('sessionToken', response.data.session_token);
        }

        return response.data;
      }

      throw new Error('No access token received');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async voiceLogin(data) {
    const formData = new FormData();
    formData.append('audio', data.voice_data);
    formData.append('device_info', JSON.stringify(data.device_info));

    const response = await api.post(`${API_BASE}/voice-login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async biometricLogin(data) {
    const response = await api.post(`${API_BASE}/biometric-login`, data);
    return response.data;
  }

  async verifyOTP(data) {
    const response = await api.post(`${API_BASE}/verify-otp`, data);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      if (response.data.session_token) {
        localStorage.setItem('sessionToken', response.data.session_token);
      }
    }
    return response.data;
  }

  async getUsernameSuggestions(name) {
    try {
      const response = await api.post(`${API_BASE}/suggest-username`, { name });
      return response.data.suggestions || [];
    } catch {
      return [];
    }
  }

  async completeLogin() {
    const response = await api.post(`${API_BASE}/complete-login`);
    return response.data;
  }

  async logout() {
    try {
      // Call logout endpoint to invalidate session
      await api.post(`${API_BASE}/logout`);
    } catch (error) {
      console.warn('Logout API call failed:', error);
    } finally {
      // Clear local storage regardless of API call result
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('sessionToken');
    }
  }

  async getCurrentUser() {
    try {
      // First check if we have a token
      const token = this.getToken();
      if (!token) {
        return null;
      }

      // Make an API call to verify the token is still valid
      const response = await api.get(`${API_BASE}/me`);
      return response.data.user;
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('sessionToken');
      return null;
    }
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }

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

  getSessionToken() {
    return localStorage.getItem('sessionToken');
  }

  async getUserProfile() {
    try {
      const response = await api.get('/user/profile');
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await api.put('/user/profile', profileData);

      // Update stored user data
      try {
        const stored = JSON.parse(localStorage.getItem('user') || 'null');
        if (stored) {
          const updatedUser = { ...stored, ...response.data.user };
          localStorage.setItem('user', JSON.stringify(updatedUser));
        }
      } catch {
        // ignore local cache update failures
      }

      return response.data;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  async changePassword(passwordData) {
    try {
      const response = await api.post('/user/change-password', passwordData);
      return response.data;
    } catch (error) {
      console.error('Error changing password:', error);
      throw error;
    }
  }

  async updatePreferences(preferences) {
    try {
      const response = await api.put('/user/preferences', preferences);

      try {
        const stored = JSON.parse(localStorage.getItem('user') || 'null');
        if (stored) {
          const updatedUser = { ...stored, preferences: response.data.preferences };
          localStorage.setItem('user', JSON.stringify(updatedUser));
        }
      } catch {
        // ignore local cache update failures
      }

      return response.data;
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  }

  async getUserActivity() {
    try {
      const response = await api.get('/user/activity');
      return response.data;
    } catch (error) {
      console.error('Error fetching user activity:', error);
      throw error;
    }
  }
}

const authService = new AuthService();
export { authService };
export default authService;