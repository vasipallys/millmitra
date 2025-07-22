import api from './api';

const API_BASE = '/auth';

class AuthService {
  async login(credentials) {
    const response = await api.post(`${API_BASE}/login`, credentials);
    return response.data;
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

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
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
      // If API call fails, fall back to localStorage but clear invalid token
      console.error('Token validation failed:', error);
      this.logout();
      return null;
    }
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export const authService = new AuthService();