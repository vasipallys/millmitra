import axios from 'axios';

const API_BASE = '/api/auth';

class AuthService {
  async login(credentials) {
    const response = await axios.post(`${API_BASE}/login`, credentials);
    return response.data;
  }

  async voiceLogin(data) {
    const formData = new FormData();
    formData.append('audio', data.voice_data);
    formData.append('device_info', JSON.stringify(data.device_info));
    
    const response = await axios.post(`${API_BASE}/voice-login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async biometricLogin(data) {
    const response = await axios.post(`${API_BASE}/biometric-login`, data);
    return response.data;
  }

  async verifyOTP(data) {
    const response = await axios.post(`${API_BASE}/verify-otp`, data);
    return response.data;
  }

  async getUsernameSuggestions(partial) {
    try {
      const response = await axios.post(`${API_BASE}/suggest-username`, { partial });
      return response.data.suggestions || [];
    } catch {
      return [];
    }
  }

  async completeLogin() {
    const response = await axios.post(`${API_BASE}/complete-login`);
    return response.data;
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export const authService = new AuthService();