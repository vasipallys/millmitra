import api from './api';

const API_BASE = '/production';

class ProductionService {
  async getBatches(params = {}) {
    const response = await api.get(`${API_BASE}/batches`, { params });
    return response.data;
  }

  async createBatch(batchData) {
    const response = await api.post(`${API_BASE}/batches`, batchData);
    return response.data;
  }

  async getBatch(batchId) {
    const response = await api.get(`${API_BASE}/batches/${batchId}`);
    return response.data;
  }

  async startBatch(batchId) {
    const response = await api.post(`${API_BASE}/batches/${batchId}/start`);
    return response.data;
  }

  async pauseBatch(batchId, data = {}) {
    const response = await api.post(`${API_BASE}/batches/${batchId}/pause`, data);
    return response.data;
  }

  async resumeBatch(batchId) {
    const response = await api.post(`${API_BASE}/batches/${batchId}/resume`);
    return response.data;
  }

  async completeBatch(batchId, completionData) {
    const response = await api.post(`${API_BASE}/batches/${batchId}/complete`, completionData);
    return response.data;
  }

  async addProductionStep(batchId, stepData) {
    const response = await api.post(`${API_BASE}/batches/${batchId}/steps`, stepData);
    return response.data;
  }

  async createQualityTest(testData) {
    const response = await api.post(`${API_BASE}/quality-tests`, testData);
    return response.data;
  }

  async getCurrentStatus() {
    const response = await api.get(`${API_BASE}/current-status`);
    return response.data;
  }

  async optimizeProduction(optimizationData) {
    const response = await api.post(`${API_BASE}/optimize`, optimizationData);
    return response.data;
  }

  async getAnalytics(days = 30) {
    const response = await api.get(`${API_BASE}/analytics?days=${days}`);
    return response.data;
  }

  async getRecommendations() {
    const response = await api.get(`${API_BASE}/recommendations`);
    return response.data;
  }
}

export const productionService = new ProductionService();