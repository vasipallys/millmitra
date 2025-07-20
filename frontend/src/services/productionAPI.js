import api from './api';

export const productionAPI = {
  // Dashboard
  getDashboard: () => api.get('/production/dashboard'),
  
  // Batches
  getBatches: (params = {}) => api.get('/production/batches', { params }),
  createBatch: (data) => api.post('/production/batches', data),
  getBatchDetails: (batchId) => api.get(`/production/batches/${batchId}`),
  startBatch: (batchId) => api.post(`/production/batches/${batchId}/start`),
  pauseBatch: (batchId, data = {}) => api.post(`/production/batches/${batchId}/pause`, data),
  resumeBatch: (batchId) => api.post(`/production/batches/${batchId}/resume`),
  completeBatch: (batchId, data) => api.post(`/production/batches/${batchId}/complete`, data),
  
  // Batch Actions
  batchAction: (batchId, action, data = {}) => {
    switch (action) {
      case 'start':
        return api.post(`/production/batches/${batchId}/start`, data);
      case 'pause':
        return api.post(`/production/batches/${batchId}/pause`, data);
      case 'resume':
        return api.post(`/production/batches/${batchId}/resume`, data);
      case 'complete':
        return api.post(`/production/batches/${batchId}/complete`, data);
      default:
        throw new Error(`Unknown batch action: ${action}`);
    }
  },
  
  // Production Steps
  addProductionStep: (batchId, data) => api.post(`/production/batches/${batchId}/steps`, data),
  
  // Quality Tests
  getQualityTests: (params = {}) => api.get('/production/quality-tests', { params }),
  createQualityTest: (data) => api.post('/production/quality-tests', data),
  
  // Production Status
  getCurrentStatus: () => api.get('/production/current-status'),
  
  // Schedules
  getSchedules: (params = {}) => api.get('/production/schedules', { params }),
  createSchedule: (data) => api.post('/production/schedules', data),
  
  // Analytics
  getAnalytics: (days = 30) => api.get('/production/analytics', { params: { days } }),
  getEfficiencyAnalysis: (params = {}) => api.get('/production/efficiency/analysis', { params }),
  
  // AI Features
  getAiRecommendations: (data) => api.post('/production/ai/recommendations', data),
  optimizeProduction: (data) => api.post('/production/optimize', data),
  
  // Maintenance
  getMaintenanceLogs: (params = {}) => api.get('/production/maintenance', { params }),
  logMaintenance: (data) => api.post('/production/maintenance', data),
  getMaintenancePredictions: () => api.get('/production/maintenance/predictions'),
  
  // Real-time updates
  subscribeToUpdates: (callback) => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`${process.env.REACT_APP_WS_URL}/production/updates`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };
    
    return () => ws.close();
  }
};

export default productionAPI;