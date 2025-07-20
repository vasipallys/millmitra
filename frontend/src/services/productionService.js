import axios from 'axios';

const API_BASE = '/api/production';

class ProductionService {
  async getBatches(params = {}) {
    const response = await axios.get(`${API_BASE}/batches`, { params });
    return response.data;
  }

  async createBatch(batchData) {
    const response = await axios.post(`${API_BASE}/batches`, batchData);
    return response.data;
  }

  async getBatch(batchId) {
    const response = await axios.get(`${API_BASE}/batches/${batchId}`);
    return response.data;
  }

  async startBatch(batchId) {
    const response = await axios.post(`${API_BASE}/batches/${batchId}/start`);
    return response.data;
  }

  async completeBatch(batchId, completionData) {
    const response = await axios.post(`${API_BASE}/batches/${batchId}/complete`, completionData);
    return response.data;
  }

  async addProductionStep(batchId, stepData) {
    const response = await axios.post(`${API_BASE}/batches/${batchId}/steps`, stepData);
    return response.data;
  }

  async createQualityTest(testData) {
    const response = await axios.post(`${API_BASE}/quality-tests`, testData);
    return response.data;
  }

  async getCurrentStatus() {
    const response = await axios.get(`${API_BASE}/current-status`);
    return response.data;
  }

  async optimizeProduction(optimizationData) {
    const response = await axios.post(`${API_BASE}/optimize`, optimizationData);
    return response.data;
  }

  async getAnalytics(days = 30) {
    const response = await axios.get(`${API_BASE}/analytics?days=${days}`);
    return response.data;
  }

  async getRecommendations() {
    const response = await axios.get(`${API_BASE}/recommendations`);
    return response.data;
  }
}

export const productionService = new ProductionService();