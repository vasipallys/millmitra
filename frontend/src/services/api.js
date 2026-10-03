import axios from 'axios';
import { attachApiTrace, endApiTrace } from '../telemetry';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    attachApiTrace(config);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    endApiTrace(response.config, response.status);
    return response;
  },
  (error) => {
    endApiTrace(error.config, error.response?.status, error);
    const url = error.config?.url || '';
    const isAuthCall = /\/auth\/(login|me|logout|verify-otp|complete-login)/.test(url);
    const data = error.response?.data;
    if (typeof data?.message === 'string' && data.message.trim()) {
      error.userMessage = data.error_id
        ? `${data.message} (ref ${data.error_id})`
        : data.message;
    } else if (typeof data?.error === 'string' && data.error.trim()) {
      error.userMessage = data.error;
    } else if (error.response?.status === 401 && isAuthCall) {
      error.userMessage = 'Username or password is not recognized';
    } else if (!error.response) {
      error.userMessage = 'Cannot reach the mill server. Confirm it is running on port 5000.';
    } else {
      error.userMessage = 'Request failed. Try again.';
    }
    if (error.response?.status === 401 && !isAuthCall) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('sessionToken');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const productionAPI = {
  getDashboard: () => api.get('/production/dashboard'),
  getBatches: (params = {}) => api.get('/production/batches', { params }),
  createBatch: (data) => api.post('/production/batches', data),
  getBatchDetails: (batchId) => api.get(`/production/batches/${batchId}`),
  startBatch: (batchId) => api.post(`/production/batches/${batchId}/start`),
  pauseBatch: (batchId, data = {}) => api.post(`/production/batches/${batchId}/pause`, data),
  resumeBatch: (batchId) => api.post(`/production/batches/${batchId}/resume`),
  completeBatch: (batchId, data) => api.post(`/production/batches/${batchId}/complete`, data),
  addProductionStep: (batchId, data) => api.post(`/production/batches/${batchId}/steps`, data),
  getQualityTests: (params = {}) => api.get('/production/quality-tests', { params }),
  createQualityTest: (data) => api.post('/production/quality-tests', data),
  getCurrentStatus: () => api.get('/production/current-status'),
  getAnalytics: (days = 30) => api.get('/production/analytics', { params: { days } }),
  getAiRecommendations: (data) => api.post('/production/ai/recommendations', data),
  optimizeProduction: (data) => api.post('/production/optimize', data),
};

export const inventoryAPI = {
  getPaddyStock: (params) => api.get('/inventory/paddy', { params }),
  getProductStock: (params) => api.get('/inventory/products', { params }),
};

export const salesAPI = {
  getCustomers: (params) => api.get('/sales/customers', { params }),
  createCustomer: (data) => api.post('/sales/customers', data),
  createOrder: (data) => api.post('/sales/orders', data),
  getOrders: (params) => api.get('/sales/orders', { params }),
  getDashboard: (days) => api.get('/sales/dashboard', { params: { days } }),
  getAnalytics: () => api.get('/sales/analytics'),
};

export default api;
